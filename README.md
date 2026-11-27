# Fenrir Wallpapers

**Library navigation:** [Documentation index](docs/README.md) · [Live volume registry](manifest/volumes.json) · [Fenrir ecosystem map](https://github.com/sunxsaturn/Fenrir-Arch/blob/main/docs/PROJECT-MAP.md) · [Desktop sync guide](https://github.com/sunxsaturn/Fenrir-Dots/blob/main/docs/WALLPAPER-LIBRARY.md)

The GitHub-hosted, rights-reviewed wallpaper collection for Fenrir Desktop.

**Collection target:** publish the largest practical number of qualifying wallpapers while keeping the complete Git repository below a conservative **900 MiB** budget. There is no fixed image count; the count depends on actual file sizes. Individual images are capped at **45 MiB** to stay below GitHub's 100 MB per-file rejection threshold.

## Repository layout

All image files belong under **[Fenrir Wallpapers/](./Fenrir%20Wallpapers/)**. The collection is divided into eight visual categories plus Unsorted.

The manifest at `manifest/index.json` records each image's SHA-256, dimensions, source, creator, license, attribution and publication-review evidence.

## Publish accepted Catalog assets

The Catalog database and quarantine are private local data and must never be committed. This repository includes a publisher that reads the Catalog's human-accepted manifest and exports only assets with a separate, explicit public-redistribution approval.

1. Clone this repository on the machine holding the local Catalog database and quarantine, then enter it:

   ```bash
   git clone --depth=1 https://github.com/sunxsaturn/Fenrir-Wallpapers.git ~/Pictures/Fenrir-Wallpapers
   cd ~/Pictures/Fenrir-Wallpapers
   ```
2. Copy `manifest/publication-approvals.example.json` to a private file, for example `~/.config/fenrir/wallpaper-publication-approvals.json`. Add one entry for every image approved for public mirroring. Each entry requires the exact license, a human reviewer and rationale, license evidence, and provider-terms evidence that permits public mirroring.
3. Run the publisher in the Python environment where `fenrir_catalog` is installed:

   ```bash
   python3 tools/publish_catalog_assets.py \
     --database "$HOME/.local/share/fenrir/catalog/catalog.sqlite3" \
     --quarantine-root "$HOME/.local/share/fenrir/catalog/quarantine" \
     --approval-file "$HOME/.config/fenrir/wallpaper-publication-approvals.json"
   ```

   The default is a read-only plan. Review the eligible count and byte estimate.
4. Add `--apply` to copy eligible files into the repository and update `manifest/index.json`.
5. Inspect the changes, then commit and push them with Git.

The publisher does not grant permission, invent rights evidence, authorize downloads, accept Catalog assets, or upload the private database/quarantine. It requires a separate human publication approval for every image. Unknown, non-commercial, no-derivatives, conflicting or undocumented rights are excluded.

## Image requirements

- Landscape, at least 2560×1440; 3840×2160 or higher preferred.
- JPEG, PNG or WebP.
- The Catalog's image validation and palette policy must already have passed.
- Exact SHA-256 and byte-size verification against the private Catalog quarantine.
- Complete source, creator, license and attribution metadata.
- Public redistribution and provider terms must independently permit publishing the original image bytes.

## Storage policy

The Volume 01 publisher and importer used a conservative **900 MiB Git object budget**. New images are capped at **45 MiB** each and duplicate SHA-256 content is skipped. One image from the initial import is approximately 69.5 MiB (below GitHub's 100 MB hard per-file limit, but above its 50 MB recommendation); it remains in history rather than rewriting the public branch. All later imports enforce the 45 MiB cap. The importer stops before exceeding the repository budget. Git history is permanent: deleting an image in a later commit does not reclaim its historical storage. Do not repeatedly replace or recompress published files; add new content as new immutable files.

This repository is public. Every committed image must be suitable for public redistribution under its documented terms.

## Fenrir integration

- Wallpaper source of truth and rights workflow: [Fenrir Wallpaper Catalog](https://github.com/sunxsaturn/Fenrir-Wallpaper-Catalog)
- Desktop consumer and rotation: [Fenrir Dots](https://github.com/sunxsaturn/Fenrir-Dots)
- Installer and deployment contract: [Fenrir Arch](https://github.com/sunxsaturn/Fenrir-Arch)

For local rotation, clone this repository and point Fenrir's wallpaper directory at the `Fenrir Wallpapers` folder (or copy its files into the configured wallpaper folder). Only committed images are public; local Catalog records remain private.

## Automated Commons population

The repository has a scheduled GitHub Actions population job. It searches Wikimedia Commons, checks each file's individual machine-readable license metadata, and downloads only original JPEG/PNG/WebP files that pass the Fenrir landscape-resolution and palette checks. The allowlist accepts CC0, public-domain, CC BY and CC BY-SA files; it rejects non-commercial and no-derivatives terms. Every image keeps its creator, source file page, license, attribution, dimensions and SHA-256 in `manifest/index.json`.

Volume 01 reached its conservative 900 MiB Git-object target with 134 published images. Its automatic acquisition schedule is now paused and the volume is retained as a read-only archive. New acquisition is active in [Volume 02](https://github.com/sunxsaturn/Fenrir-Wallpapers-02), which has its own 8 GiB object-store target. The hub registry at `manifest/volumes.json` lists every part of the combined collection; live image counts are read from each volume manifest.

Wikimedia Commons notes that each file has its own reuse requirements and that reusers should verify licensing information and comply with attribution and license terms. Automated metadata checks are a screening aid, not a legal warranty. Review the linked file page and any additional rights notices before relying on an image; files with uncertain or incompatible metadata are excluded. See [Commons reuse guidance](https://commons.wikimedia.org/wiki/Commons:Reusing_content_outside_Wikimedia/en).

## Multi-repository library (volumes)

This repository is the library hub and **Volume 01**. The live volume registry is `manifest/volumes.json`; clients should read that registry rather than hard-code a list of wallpaper repositories. New repositories will use the names `Fenrir-Wallpapers-02`, `Fenrir-Wallpapers-03`, and so on, each with the same `Fenrir Wallpapers/` category layout and its own `manifest/index.json`.

The initial Volume 01 was deliberately kept near a conservative 900 MiB object-store budget. For future volumes, the target is **8 GiB per repository**, below GitHub's current 10 GB recommended on-disk size. New images are capped at 45 MiB and upload batches stay well below GitHub's 2 GB push limit. These are operating targets, not a claim that GitHub offers unlimited aggregate storage. See [GitHub repository limits](https://docs.github.com/en/repositories/creating-and-managing-repositories/repository-limits).

A single sequential acquisition coordinator will manage the volume registry and write each validated image to the active volume. Do not run independent Wikimedia downloaders concurrently across volumes: Wikimedia applies API rate limits globally and asks clients to identify themselves, keep concurrency low, and obey `Retry-After`. Each file still needs its own valid reuse terms and attribution; splitting repositories does not change licensing or raise source rate limits. See [Wikimedia API rate limits](https://www.mediawiki.org/wiki/Wikimedia_APIs/Rate_limits).

Fenrir Desktop should sync all registered volumes into one local wallpaper root. Its recursive image scanner can then treat the combined directory tree as one collection.

