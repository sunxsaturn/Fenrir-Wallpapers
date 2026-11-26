#!/usr/bin/env python3
"""Publish explicitly approved, human-accepted Catalog images into this Git repo.

Default mode is read-only. --apply copies verified image bytes and updates the
public attribution index. It never downloads, authorizes, accepts, or changes
Catalog records.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from fenrir_catalog.library import build_library_manifest
from fenrir_catalog.consumer import read_manifest_asset

REPOSITORY = "sunxsaturn/Fenrir-Wallpapers"
IMAGE_ROOT = Path("Fenrir Wallpapers")
INDEX_PATH = Path("manifest/index.json")
MAX_REPOSITORY_BYTES = 900 * 1024 * 1024
MAX_IMAGE_BYTES = 95 * 1024 * 1024
PAGE_SIZE = 500
LICENSES = {"CC0-1.0", "CC-BY-4.0", "CC-BY-SA-4.0"}
MIME_SUFFIX = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}
CATEGORIES = {
    "nordic-mythology-fantasy", "cinematic-nature", "cosmic-science-fiction",
    "arctic-blue-violet", "monochrome-futuristic-architecture",
    "red-violet-dark-fantasy", "deep-ocean-bioluminescence",
    "obsidian-minimalism-abstract-geometry", "unsorted",
}


def fail(message: str) -> None:
    raise SystemExit(f"publish_catalog_assets: {message}")


def https_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc)


def load_approvals(path: Path) -> dict[str, dict]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        fail(f"cannot read approval file: {exc}")
    approvals = payload.get("approvals") if isinstance(payload, dict) else None
    if not isinstance(approvals, list):
        fail("approval file must contain an 'approvals' array")
    result: dict[str, dict] = {}
    for item in approvals:
        if not isinstance(item, dict):
            fail("every approval must be a JSON object")
        asset_id = item.get("asset_id")
        if not isinstance(asset_id, str) or not asset_id or asset_id in result:
            fail("approval asset_id values must be non-empty and unique")
        if item.get("redistribution_permitted") is not True:
            fail(f"{asset_id}: redistribution_permitted must be explicitly true")
        if item.get("provider_terms_permit_public_mirroring") is not True:
            fail(f"{asset_id}: provider terms must explicitly permit public mirroring")
        if item.get("license_identifier") not in LICENSES:
            fail(f"{asset_id}: license must be one of {sorted(LICENSES)}")
        if not https_url(item.get("license_evidence_url")):
            fail(f"{asset_id}: HTTPS license_evidence_url is required")
        if not https_url(item.get("provider_terms_evidence_url")):
            fail(f"{asset_id}: HTTPS provider_terms_evidence_url is required")
        for field in ("reviewer", "rationale"):
            value = item.get(field)
            if not isinstance(value, str) or not value.strip():
                fail(f"{asset_id}: {field} is required")
        category = item.get("category", "unsorted")
        if category not in CATEGORIES:
            fail(f"{asset_id}: unsupported category {category!r}")
        result[asset_id] = item
    return result


def git_output(root: Path, *args: str) -> str:
    try:
        result = subprocess.run(
            ["git", *args], cwd=root, check=True, capture_output=True, text=True
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        fail(f"Git command failed ({' '.join(args)}): {exc}")
    return result.stdout.strip()


def check_repository(root: Path) -> None:
    top = Path(git_output(root, "rev-parse", "--show-toplevel")).resolve()
    if top != root.resolve():
        fail("--repo-root must be the root of the wallpaper repository")
    remote = git_output(root, "remote", "get-url", "origin")
    valid = {
        "https://github.com/" + REPOSITORY + ".git",
        "https://github.com/" + REPOSITORY,
        "git@github.com:" + REPOSITORY + ".git",
    }
    if remote not in valid:
        fail(f"origin must point to {REPOSITORY}; found {remote!r}")


def git_object_bytes(root: Path) -> int:
    output = git_output(root, "count-objects", "-v")
    values = {}
    for line in output.splitlines():
        key, sep, value = line.partition(":")
        if sep:
            values[key.strip()] = value.strip()
    try:
        return (int(values.get("size", "0")) + int(values.get("size-pack", "0"))) * 1024
    except ValueError:
        fail("could not parse Git object-store size")


def load_index(root: Path) -> dict:
    path = root / INDEX_PATH
    if not path.exists():
        return {"schema": "org.fenrir.public-wallpapers.index.v1", "updated_at": None, "count": 0, "items": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        fail(f"existing manifest index is invalid: {exc}")
    if not isinstance(data, dict) or data.get("schema") != "org.fenrir.public-wallpapers.index.v1" or not isinstance(data.get("items"), list):
        fail("existing manifest/index.json has an unsupported structure")
    return data


def collect_catalog_pages(database: Path, quarantine: Path, approvals: dict[str, dict], root: Path):
    cursor = None
    candidates = []
    accepted_ids = set()
    reasons: dict[str, int] = {}
    existing_index = load_index(root)
    existing_shas = {
        item.get("sha256") for item in existing_index["items"]
        if isinstance(item, dict) and isinstance(item.get("sha256"), str)
    }
    for _page_number in range(10000):
        manifest = build_library_manifest(database, limit=PAGE_SIZE, cursor=cursor)
        if manifest.get("scope") != "human-accepted-catalog-assets":
            fail("Catalog returned an unexpected manifest scope")
        results = manifest.get("results")
        if not isinstance(results, list):
            fail("Catalog returned an invalid manifest page")
        for item in results:
            asset_id = item.get("asset_id")
            if not isinstance(asset_id, str):
                continue
            accepted_ids.add(asset_id)
            approval = approvals.get(asset_id)
            if approval is None:
                continue
            metadata = item.get("metadata") or {}
            rights = item.get("rights") or {}
            provenance = item.get("provenance") or {}
            integrity = item.get("integrity") or {}
            width, height = metadata.get("width"), metadata.get("height")
            mime = metadata.get("mime_type")
            sha = integrity.get("sha256")
            size = integrity.get("file_size_bytes")
            checks = [
                (rights.get("rights_status") == "human_approved", "catalog_rights_not_human_approved"),
                (rights.get("license_decision") == "approved", "catalog_license_not_approved"),
                (rights.get("license_identifier") == approval.get("license_identifier"), "license_mismatch"),
                (approval.get("license_identifier") in LICENSES, "license_not_allowlisted"),
                (isinstance(width, int) and isinstance(height, int) and width >= 2560 and height >= 1440 and width > height, "resolution_or_orientation"),
                (mime in MIME_SUFFIX, "unsupported_mime_type"),
                (isinstance(sha, str) and re.fullmatch(r"[0-9a-f]{64}", sha) is not None, "invalid_sha256"),
                (isinstance(size, int) and 0 < size <= MAX_IMAGE_BYTES, "image_size_limit"),
                (https_url(provenance.get("source_url")), "missing_https_source_url"),
                (https_url(rights.get("license_url")), "missing_https_license_url"),
                (isinstance(metadata.get("creator"), str) and bool(metadata.get("creator", "").strip()), "missing_creator"),
                (isinstance(rights.get("attribution_text"), str) and bool(rights.get("attribution_text", "").strip()), "missing_attribution"),
            ]
            failed = [reason for passed, reason in checks if not passed]
            if failed:
                for reason in failed:
                    reasons[reason] = reasons.get(reason, 0) + 1
                continue
            if sha in existing_shas:
                reasons["duplicate_sha256_already_published"] = reasons.get("duplicate_sha256_already_published", 0) + 1
                continue
            category = approval.get("category", "unsorted")
            destination = IMAGE_ROOT / category / (sha + MIME_SUFFIX[mime])
            candidates.append((manifest, item, approval, destination, size))
            existing_shas.add(sha)
        cursor = manifest.get("next_cursor")
        if not cursor:
            break
    else:
        fail("Catalog pagination exceeded its safety bound")
    unknown_approvals = sorted(set(approvals) - accepted_ids)
    return candidates, reasons, unknown_approvals


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--quarantine-root", type=Path, required=True)
    parser.add_argument("--approval-file", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--apply", action="store_true", help="write verified images and update the index; default is read-only")
    args = parser.parse_args()

    root = args.repo_root.expanduser().resolve()
    database = args.database.expanduser().resolve()
    quarantine = args.quarantine_root.expanduser().resolve()
    if not database.is_file() or not quarantine.is_dir():
        fail("database must be an existing file and quarantine root an existing directory")
    if Path("/mnt/storage") in (database, *database.parents) or Path("/mnt/storage") in (quarantine, *quarantine.parents):
        fail("Catalog database and quarantine under /mnt/storage are not permitted")
    check_repository(root)

    approvals = load_approvals(args.approval_file.expanduser())
    if not approvals:
        fail("approval file contains no publication approvals")

    candidates, reasons, unknown = collect_catalog_pages(database, quarantine, approvals, root)
    current_bytes = git_object_bytes(root)
    new_bytes = sum(candidate[4] for candidate in candidates)
    reserve_bytes = 2 * 1024 * 1024
    projected = current_bytes + new_bytes + reserve_bytes
    report = {
        "mode": "apply" if args.apply else "read_only_plan",
        "approved_entries_in_file": len(approvals),
        "eligible_images": len(candidates),
        "eligible_image_bytes": new_bytes,
        "git_object_bytes_before": current_bytes,
        "projected_git_object_bytes_with_reserve": projected,
        "repository_budget_bytes": MAX_REPOSITORY_BYTES,
        "per_image_limit_bytes": MAX_IMAGE_BYTES,
        "blocked_or_skipped": reasons,
        "approval_asset_ids_not_found_in_accepted_catalog": unknown,
        "writes_performed": False,
        "downloads_started": 0,
        "catalog_records_changed": 0,
    }
    print(json.dumps(report, indent=2))
    if not args.apply:
        print("Read-only plan only. Add --apply after reviewing the report.")
        return 0
    if projected > MAX_REPOSITORY_BYTES:
        fail("projected Git object store exceeds the 900 MiB repository budget; publish a smaller batch")
    if not candidates:
        print("No new eligible images to publish.")
        return 0

    index = load_index(root)
    indexed_ids = {item.get("asset_id") for item in index["items"] if isinstance(item, dict)}
    added = []
    for manifest, item, approval, relative_path, expected_size in candidates:
        asset_id = item["asset_id"]
        if asset_id in indexed_ids:
            continue
        content = read_manifest_asset(manifest, asset_id, quarantine, max_bytes=MAX_IMAGE_BYTES)
        digest = hashlib.sha256(content).hexdigest()
        if digest != item["integrity"]["sha256"] or len(content) != expected_size:
            fail(f"{asset_id}: final content integrity check failed")
        destination = root / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            fail(f"destination already exists but is not indexed: {relative_path}")
        destination.write_bytes(content)
        metadata = item["metadata"]
        rights = item["rights"]
        provenance = item["provenance"]
        added.append({
            "asset_id": asset_id,
            "path": relative_path.as_posix(),
            "sha256": digest,
            "file_size_bytes": len(content),
            "mime_type": metadata["mime_type"],
            "width": metadata["width"],
            "height": metadata["height"],
            "title": metadata.get("title"),
            "creator": metadata["creator"],
            "attribution": rights["attribution_text"],
            "source_url": provenance["source_url"],
            "license_identifier": rights["license_identifier"],
            "license_url": rights["license_url"],
            "publication_review": {
                "reviewer": approval["reviewer"],
                "rationale": approval["rationale"],
                "license_evidence_url": approval["license_evidence_url"],
                "provider_terms_evidence_url": approval["provider_terms_evidence_url"],
                "redistribution_permitted": True,
                "provider_terms_permit_public_mirroring": True,
            },
        })
        indexed_ids.add(asset_id)

    index["items"].extend(added)
    index["count"] = len(index["items"])
    index["updated_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    index_path = root / INDEX_PATH
    index_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = index_path.with_name(index_path.name + ".tmp")
    temporary.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(index_path)

    print(json.dumps({
        "published_to_working_tree": len(added),
        "published_bytes": sum(item["file_size_bytes"] for item in added),
        "manifest_index": str(INDEX_PATH),
        "git_commit_or_push_performed": False,
        "next_step": "Review git diff, then commit and push the image files and manifest.",
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
