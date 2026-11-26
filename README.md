# Fenrir Wallpapers

The GitHub-hosted, rights-reviewed wallpaper collection for Fenrir Desktop.

**Collection target:** publish the largest practical number of qualifying wallpapers while keeping the complete Git repository below a conservative **900 MiB** budget. There is no fixed image count; the count depends on actual file sizes. Individual images are capped at **95 MiB** to stay below GitHub's 100 MB per-file rejection threshold.

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

The publisher uses a conservative **900 MiB Git object budget** and a **95 MiB per-image ceiling**. It skips duplicate SHA-256 content and stops before exceeding the budget. Git history is permanent: deleting an image in a later commit does not reclaim its historical storage. Do not repeatedly replace or recompress published files; add new content as new immutable files.

This repository is public. Every committed image must be suitable for public redistribution under its documented terms.

## Fenrir integration

- Wallpaper source of truth and rights workflow: [Fenrir Wallpaper Catalog](https://github.com/sunxsaturn/Fenrir-Wallpaper-Catalog)
- Desktop consumer and rotation: [Fenrir Dots](https://github.com/sunxsaturn/Fenrir-Dots)
- Installer and deployment contract: [Fenrir Arch](https://github.com/sunxsaturn/Fenrir-Arch)

For local rotation, clone this repository and point Fenrir's wallpaper directory at the `Fenrir Wallpapers` folder (or copy its files into the configured wallpaper folder). Only committed images are public; local Catalog records remain private.
