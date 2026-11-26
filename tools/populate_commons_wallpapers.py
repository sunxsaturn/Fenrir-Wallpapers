#!/usr/bin/env python3
"""Populate the Fenrir image repository from individually licensed Commons files.

Only original files with explicit free/public-domain license metadata are
considered. Full-resolution bytes are validated before publication. The job
keeps the 900 MiB Git-object budget, tracks attribution, and never uploads
Catalog databases or private quarantine data.
"""
from __future__ import annotations

import argparse
import colorsys
import hashlib
import html
import io
import json
import re
import time
import warnings
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from PIL import Image, ImageOps

API = "https://commons.wikimedia.org/w/api.php"
USER_AGENT = (
    "FenrirWallpaperLibrary/1.0 "
    "(https://github.com/sunxsaturn/Fenrir-Wallpapers; "
    "Commons reuse with per-file attribution)"
)
ROOT = Path.cwd()
IMAGE_ROOT = ROOT / "Fenrir Wallpapers"
INDEX_PATH = ROOT / "manifest/index.json"
MAX_REPOSITORY_BYTES = 900 * 1024 * 1024
MAX_IMAGE_BYTES = 95 * 1024 * 1024
MAX_DOWNLOAD_BYTES_PER_RUN = 250 * 1024 * 1024
MAX_DOWNLOAD_ATTEMPTS_PER_RUN = 80
PAGE_SIZE = 50
PER_CATEGORY_LIMIT = 3
MIME_SUFFIX = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}
CATEGORIES = {
    "nordic-mythology-fantasy": [
        "Norse mythology",
        "Viking ship landscape",
        "Viking age archaeology",
    ],
    "cinematic-nature": [
        "fjord mountain landscape",
        "mountain range landscape",
        "waterfall forest landscape",
    ],
    "cosmic-science-fiction": [
        "nebula galaxy astrophotography",
        "Milky Way night sky",
        "planet astronomy space",
    ],
    "arctic-blue-violet": [
        "aurora borealis landscape",
        "glacier ice field landscape",
        "iceberg Antarctica landscape",
    ],
    "monochrome-futuristic-architecture": [
        "brutalist architecture",
        "modern architecture geometric facade",
        "concrete architecture monochrome",
    ],
    "red-violet-dark-fantasy": [
        "volcanic landscape",
        "red rock canyon landscape",
        "red nebula astronomy",
    ],
    "deep-ocean-bioluminescence": [
        "bioluminescence underwater",
        "deep sea underwater landscape",
        "underwater ocean photography",
    ],
    "obsidian-minimalism-abstract-geometry": [
        "abstract black geometric sculpture",
        "minimalist brutalist architecture",
        "modern architecture geometric minimalism",
    ],
}
LICENSE_RE = re.compile(r"^CC BY(?:-SA)?(?:\s|$)", re.IGNORECASE)
SHA_RE = re.compile(r"^[0-9a-f]{64}$")


class TextOnly(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def clean(value: object) -> str:
    if isinstance(value, dict):
        value = value.get("value", "")
    if not isinstance(value, str):
        return ""
    parser = TextOnly()
    try:
        parser.feed(value)
        parser.close()
        return " ".join(html.unescape(" ".join(parser.parts)).split())
    except Exception:
        return " ".join(re.sub(r"<[^>]*>", " ", html.unescape(value)).split())


def get_json(url: str) -> dict:
    request = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        },
    )
    with urlopen(request, timeout=45) as response:
        payload = response.read(12 * 1024 * 1024 + 1)
    if len(payload) > 12 * 1024 * 1024:
        raise ValueError("Commons API response exceeded 12 MiB")
    value = json.loads(payload)
    if not isinstance(value, dict):
        raise ValueError("Commons API returned a non-object response")
    if "error" in value:
        raise ValueError(f"Commons API error: {value['error']}")
    return value


def fetch_search_page(query: str, offset: int) -> list[dict]:
    params = {
        "action": "query",
        "format": "json",
        "formatversion": "2",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": "6",
        "gsrlimit": str(PAGE_SIZE),
        "gsroffset": str(offset),
        "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata",
    }
    url = API + "?" + urlencode(params)
    data = get_json(url)
    query_data = data.get("query", {})
    pages = query_data.get("pages", [])
    return pages if isinstance(pages, list) else []


def license_details(ext: dict) -> tuple[str, str] | None:
    name = clean(ext.get("LicenseShortName"))
    lowered = name.lower()
    license_url = clean(ext.get("LicenseUrl"))
    if "non-commercial" in lowered or "noncommercial" in lowered:
        return None
    if re.search(r"\bNC\b|\bND\b", name, re.IGNORECASE):
        return None
    if lowered.startswith("cc0"):
        return name, license_url or "https://creativecommons.org/publicdomain/zero/1.0/"
    if lowered == "public domain" or lowered.startswith("pd-"):
        return name, license_url or "https://commons.wikimedia.org/wiki/Commons:Public_domain"
    if LICENSE_RE.match(name):
        if not license_url.startswith("https://"):
            return None
        return name, license_url
    return None


def image_bytes(url: str) -> bytes:
    if not url.startswith("https://"):
        raise ValueError("image URL is not HTTPS")
    request = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "image/jpeg,image/png,image/webp",
        },
    )
    with urlopen(request, timeout=90) as response:
        content_type = response.headers.get_content_type().lower()
        if content_type not in MIME_SUFFIX:
            raise ValueError(f"unsupported response MIME type: {content_type}")
        content_length = response.headers.get("Content-Length")
        if content_length and int(content_length) > MAX_IMAGE_BYTES:
            raise ValueError("image exceeds per-file size limit")
        payload = response.read(MAX_IMAGE_BYTES + 1)
    if not payload or len(payload) > MAX_IMAGE_BYTES:
        raise ValueError("image is empty or exceeds per-file size limit")
    return payload


def color_family(rgb: tuple[int, int, int]) -> str:
    red, green, blue = (channel / 255.0 for channel in rgb)
    hue, saturation, brightness = colorsys.rgb_to_hsv(red, green, blue)
    degrees = hue * 360.0
    if brightness >= 0.88 and saturation <= 0.20:
        return "white"
    if saturation <= 0.18:
        return "black" if brightness <= 0.14 else "neutral"
    if degrees < 15 or degrees >= 345:
        return "red"
    if 15 <= degrees < 43:
        return "brown" if brightness <= 0.78 else "orange"
    if 43 <= degrees < 70:
        return "yellow"
    if 70 <= degrees < 165:
        return "green"
    if 165 <= degrees < 260:
        return "blue"
    if 260 <= degrees < 330:
        return "purple"
    return "red"


def validate_image(payload: bytes, mime: str) -> tuple[int, int, list[str]]:
    with warnings.catch_warnings():
        warnings.simplefilter("error", Image.DecompressionBombWarning)
        with Image.open(io.BytesIO(payload)) as source:
            if source.format not in {"JPEG", "PNG", "WEBP"}:
                raise ValueError("decoded image format is not JPEG, PNG or WebP")
            image = ImageOps.exif_transpose(source)
            width, height = image.size
            if width < 2560 or height < 1440 or width <= height:
                raise ValueError("image does not meet 2560x1440 landscape minimum")
            image.load()
            sample = image.convert("RGB")
            sample.thumbnail((128, 128), Image.Resampling.BOX)
            colors = sample.getcolors(maxcolors=128 * 128)
            if colors is None:
                raise ValueError("could not compute bounded palette")
            dominant = sorted(colors, key=lambda row: (-row[0], row[1]))[:5]
            hex_colors = [
                "#" + "".join(f"{channel:02x}" for channel in rgb)
                for _count, rgb in dominant
            ]
            families = {color_family(rgb) for _count, rgb in dominant}
            excluded = families.intersection({"yellow", "orange", "brown"})
            if excluded:
                raise ValueError("image violates Fenrir palette policy: " + ",".join(sorted(excluded)))
            expected = {
                "JPEG": "image/jpeg",
                "PNG": "image/png",
                "WEBP": "image/webp",
            }[source.format]
            if expected != mime:
                raise ValueError("decoded format does not match Commons MIME metadata")
    return width, height, hex_colors


def load_index() -> dict:
    try:
        payload = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        payload = {
            "schema": "org.fenrir.public-wallpapers.index.v1",
            "updated_at": None,
            "count": 0,
            "search_state": {},
            "items": [],
        }
    if (
        not isinstance(payload, dict)
        or payload.get("schema") != "org.fenrir.public-wallpapers.index.v1"
        or not isinstance(payload.get("items"), list)
    ):
        raise ValueError("existing manifest/index.json has an invalid schema")
    if not isinstance(payload.get("search_state", {}), dict):
        payload["search_state"] = {}
    return payload


def git_object_bytes() -> int:
    import subprocess

    result = subprocess.run(
        ["git", "count-objects", "-v"],
        check=True,
        text=True,
        capture_output=True,
    )
    values = {}
    for line in result.stdout.splitlines():
        key, sep, value = line.partition(":")
        if sep:
            values[key.strip()] = value.strip()
    return (
        int(values.get("size", "0")) + int(values.get("size-pack", "0"))
    ) * 1024


def commons_page_url(title: str) -> str:
    return "https://commons.wikimedia.org/wiki/" + quote(title.replace(" ", "_"), safe="()_:")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-new-images", type=int, default=24)
    args = parser.parse_args()
    if not 1 <= args.max_new_images <= 40:
        raise SystemExit("--max-new-images must be between 1 and 40")

    index = load_index()
    existing_shas = {
        item.get("sha256")
        for item in index["items"]
        if isinstance(item, dict) and isinstance(item.get("sha256"), str)
    }
    existing_titles = {
        item.get("commons_title")
        for item in index["items"]
        if isinstance(item, dict) and isinstance(item.get("commons_title"), str)
    }
    search_state = index["search_state"]
    start_size = git_object_bytes()
    available_budget = MAX_REPOSITORY_BYTES - start_size
    if available_budget <= 2 * 1024 * 1024:
        print(json.dumps({"status": "repository_budget_reached", "git_object_bytes": start_size}))
        return 0

    accepted: list[dict] = []
    added_bytes = 0
    download_attempts = 0
    rejected: dict[str, int] = {}
    failures: list[str] = []

    def reject(reason: str) -> None:
        rejected[reason] = rejected.get(reason, 0) + 1

    for category, queries in CATEGORIES.items():
        if len(accepted) >= args.max_new_images or added_bytes >= MAX_DOWNLOAD_BYTES_PER_RUN:
            break
        state = search_state.get(category, {})
        if not isinstance(state, dict):
            state = {}
        query_index = int(state.get("query_index", 0)) % len(queries)
        offset = max(0, int(state.get("offset", 0)))
        if offset >= 500:
            query_index = (query_index + 1) % len(queries)
            offset = 0
        query_text = queries[query_index]
        try:
            pages = fetch_search_page(query_text, offset)
        except Exception as exc:
            failures.append(f"{category}: search failed: {str(exc)[:200]}")
            time.sleep(1.1)
            continue

        category_added = 0
        for page in pages:
            if len(accepted) >= args.max_new_images or category_added >= PER_CATEGORY_LIMIT:
                break
            if download_attempts >= MAX_DOWNLOAD_ATTEMPTS_PER_RUN or added_bytes >= MAX_DOWNLOAD_BYTES_PER_RUN:
                break
            title = page.get("title")
            infos = page.get("imageinfo")
            if not isinstance(title, str) or not isinstance(infos, list) or not infos:
                reject("missing_imageinfo")
                continue
            if title in existing_titles:
                reject("already_published_title")
                continue
            info = infos[0]
            if not isinstance(info, dict):
                reject("invalid_imageinfo")
                continue
            mime = str(info.get("mime", "")).lower()
            suffix = MIME_SUFFIX.get(mime)
            if suffix is None:
                reject("unsupported_mime")
                continue
            width = info.get("width")
            height = info.get("height")
            size = info.get("size")
            if not (
                isinstance(width, int) and isinstance(height, int)
                and width >= 2560 and height >= 1440 and width > height
            ):
                reject("metadata_dimensions")
                continue
            if not isinstance(size, int) or size <= 0 or size > MAX_IMAGE_BYTES:
                reject("metadata_file_size")
                continue
            ext = info.get("extmetadata", {})
            if not isinstance(ext, dict):
                reject("missing_license_metadata")
                continue
            license_info = license_details(ext)
            if license_info is None:
                reject("license_not_allowlisted")
                continue
            license_name, license_url = license_info
            creator = clean(ext.get("Artist"))
            credit = clean(ext.get("Credit"))
            description = clean(ext.get("ImageDescription"))
            if not creator:
                creator = credit
            if not creator:
                reject("missing_creator_attribution")
                continue
            image_url = info.get("url")
            if not isinstance(image_url, str):
                reject("missing_original_url")
                continue
            if image_url.startswith("http://"):
                image_url = "https://" + image_url[len("http://"):]
            if not image_url.startswith("https://"):
                reject("non_https_original_url")
                continue

            download_attempts += 1
            try:
                payload = image_bytes(image_url)
                if len(payload) > MAX_DOWNLOAD_BYTES_PER_RUN - added_bytes:
                    reject("run_download_budget_reached")
                    break
                real_width, real_height, colors = validate_image(payload, mime)
            except Exception as exc:
                reject("download_or_validation_failed")
                failures.append(f"{title}: {str(exc)[:200]}")
                time.sleep(0.35)
                continue
            if len(payload) > available_budget - added_bytes - 2 * 1024 * 1024:
                reject("repository_budget_would_be_exceeded")
                continue

            digest = hashlib.sha256(payload).hexdigest()
            if digest in existing_shas:
                reject("duplicate_sha256")
                continue
            filename = digest + suffix
            relative_path = Path("Fenrir Wallpapers") / category / filename
            destination = ROOT / relative_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            if destination.exists():
                reject("destination_exists")
                continue
            destination.write_bytes(payload)

            artist_credit = credit or creator
            attribution = (
                f"{artist_credit}. {title.removeprefix('File:')} "
                f"via Wikimedia Commons. License: {license_name}."
            )
            accepted.append({
                "path": relative_path.as_posix(),
                "sha256": digest,
                "file_size_bytes": len(payload),
                "mime_type": mime,
                "width": real_width,
                "height": real_height,
                "dominant_colors": colors,
                "title": title.removeprefix("File:"),
                "description": description,
                "creator": creator,
                "credit": artist_credit,
                "attribution": attribution,
                "source": "Wikimedia Commons",
                "source_page": commons_page_url(title),
                "original_file_url": image_url,
                "license_identifier": license_name,
                "license_url": license_url,
                "license_review": "automated metadata gate; verify file page for corrections",
                "publication_policy": "CC0/Public Domain/CC BY/CC BY-SA; NC and ND excluded",
            })
            existing_shas.add(digest)
            existing_titles.add(title)
            added_bytes += len(payload)
            category_added += 1
            time.sleep(0.35)

        # Advance the bounded search cursor even when a page had no eligible
        # candidates, so later scheduled runs explore more of the source.
        next_offset = offset + PAGE_SIZE
        next_query_index = query_index
        if not pages or next_offset >= 500:
            next_query_index = (query_index + 1) % len(queries)
            next_offset = 0
        search_state[category] = {
            "query_index": next_query_index,
            "offset": next_offset,
            "last_query": query_text,
        }
        time.sleep(1.1)

    if accepted:
        index["items"].extend(accepted)
        index["items"].sort(key=lambda item: item.get("path", ""))
        index["count"] = len(index["items"])
        index["search_state"] = search_state
        index["updated_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
        temporary = INDEX_PATH.with_name(INDEX_PATH.name + ".tmp")
        temporary.write_text(
            json.dumps(index, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        temporary.replace(INDEX_PATH)
    else:
        # Persist cursors to ensure subsequent scheduled runs move forward.
        index["search_state"] = search_state
        INDEX_PATH.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = {
        "status": "images_added" if accepted else "no_eligible_images_this_run",
        "new_images": len(accepted),
        "new_image_bytes": added_bytes,
        "total_manifest_images": len(index["items"]),
        "git_object_bytes_before": start_size,
        "repository_budget_bytes": MAX_REPOSITORY_BYTES,
        "download_attempts": download_attempts,
        "rejected": rejected,
        "source": "Wikimedia Commons",
        "failures": failures[:20],
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
