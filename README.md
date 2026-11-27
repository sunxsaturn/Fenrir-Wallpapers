# Fenrir Wallpapers

**Library navigation:** [Documentation index](docs/README.md) · [Live volume registry](manifest/volumes.json) · [Fenrir ecosystem map](https://github.com/sunxsaturn/Fenrir-Arch/blob/main/docs/PROJECT-MAP.md) · [Desktop sync guide](https://github.com/sunxsaturn/Fenrir-Dots/blob/main/docs/WALLPAPER-LIBRARY.md)

The public wallpaper library for Fenrir Desktop. This repository is both the library hub and **Volume 01**. The hub registry defines which numbered repositories participate in the combined library and is the source of truth for their current roles and status.

## Start here

- Read the [library documentation index](docs/README.md).
- Inspect the [live volume registry](manifest/volumes.json) before population or synchronization.
- Read [Fenrir Dots' sync guide](https://github.com/sunxsaturn/Fenrir-Dots/blob/main/docs/WALLPAPER-LIBRARY.md) to mirror active volumes into one local rotation directory.
- Read [Fenrir's project map](https://github.com/sunxsaturn/Fenrir-Arch/blob/main/docs/PROJECT-MAP.md) to understand how the public library relates to the private Catalog and desktop.

## Registered volumes

The current registry lists three active volumes:

| Volume | Repository | Registry role | Acquisition state |
|---|---|---|---|
| 01 | [Fenrir-Wallpapers](https://github.com/sunxsaturn/Fenrir-Wallpapers) | Hub and archived image volume · 134 images | Closed |
| 02 | [Fenrir-Wallpapers-02](https://github.com/sunxsaturn/Fenrir-Wallpapers-02) | Published image volume · 1,132 images | Closed |
| 03 | [Fenrir-Wallpapers-03](https://github.com/sunxsaturn/Fenrir-Wallpapers-03) | Published image volume · 605 images | Closed |

All three remain active for desktop synchronization, but every volume is closed to acquisition. The registry's `active` field controls what clients sync; `acquisition_enabled: false` and `status: closed` mean no further population is scheduled.

The live manifests contain **1,871 published image records** across the three volumes. The hub registry records a 2026-11-27 snapshot of **1,871 unique SHA-256 identifiers and no cross-volume duplicates**. All nine category folders already exist; the current distribution is intentionally preserved rather than equalized to an arbitrary count. Manifests remain authoritative for live image records and counts; the hub registry is authoritative for repository discovery and population state. Desktop clients must read the registry instead of hard-coding volume names or counts.

## Public publishing rules

This repository is public. Every committed image must have independent public-redistribution clearance, a compatible license and provider terms permitting public mirroring. Preserve creator, credit, source page, license and attribution metadata in the relevant volume manifest.

The private Catalog's database and quarantine must never be committed. Catalog acceptance and local desktop sync do not, by themselves, authorize public publication. The publisher requires a separate, explicit per-asset publication approval.

See [Publish accepted Catalog assets](#publish-accepted-catalog-assets) and the [source policy in the private Catalog](https://github.com/sunxsaturn/Fenrir-Wallpaper-Catalog/blob/main/docs/SOURCES.md).

## Publish accepted Catalog assets

The publisher reads a human-accepted Catalog manifest and exports only assets with a distinct public-publication approval.

1. Clone this repository on the machine that holds the private Catalog database and quarantine.
2. Copy `manifest/publication-approvals.example.json` to a private approval file and record the exact license, reviewer, rationale, license evidence and provider-terms evidence for each asset.
3. Run `tools/publish_catalog_assets.py` without `--apply` first; review its read-only eligibility and byte report.
4. Add `--apply` only after reviewing the plan, then inspect the image and manifest changes before committing.

The publisher does not create rights evidence, authorize downloads, accept assets, or upload private database/quarantine data. Unknown, conflicting, non-commercial, no-derivatives or undocumented rights are excluded.

## Population status — closed

The public library is now an existing-assets-only archive. **No further source acquisition, count-based balancing, category quotas or new volume creation is scheduled.** The three registered volumes remain active for desktop synchronization.

The point-in-time category inventory recorded on 2026-11-27 is:

| Category | Published images |
|---|---:|
| Arctic Blue/Violet | 228 |
| Cinematic Nature | 228 |
| Cosmic Science Fiction | 228 |
| Deep Ocean/Bioluminescence | 221 |
| Monochrome Futuristic Architecture | 228 |
| Nordic Mythology/Fantasy | 228 |
| Obsidian Minimalism/Abstract Geometry | 171 |
| Red/Violet Dark Fantasy | 228 |
| Unsorted | 111 |
| **Total** | **1,871** |

These figures are a dated snapshot, not targets. No images are deleted, overwritten, duplicated or moved to make the table look balanced. The remaining 7 / 57 / 117 differences are retained as they are; population is closed without trying to fill them from new sources.

The scheduled/dispatch acquisition workflows for Volumes 02 and 03 have been removed. The hub registry now marks all three volumes active for sync and closed for acquisition. There is no Volume 04 plan.

For a current read-only manifest audit, use `fenrir-wallpaper audit-library --json` from a current Fenrir Dots release. The audit reads the hub registry and each active manifest; it does not fetch image bytes or inspect a local directory. The desktop sync client verifies image bytes separately when downloading. Use `fenrir-wallpaper sync-library --dry-run` before an explicitly confirmed local synchronization.

## Immutable history and rights

Git history is persistent. Existing content-addressed files and their manifests are retained. Do not repeatedly replace, recompress, move or delete committed images. Existing redistribution terms and attribution requirements continue to apply; publication does not grant additional rights.

`docs/POPULATION-STATUS.md` records the closure and inventory snapshot. The live registry remains the source of truth for active repositories and population state.

## Fenrir integration

- Private discovery, rights evidence, acquisition and acceptance: [Fenrir Wallpaper Catalog](https://github.com/sunxsaturn/Fenrir-Wallpaper-Catalog)
- Desktop UI, local rotation and multi-volume sync: [Fenrir Dots](https://github.com/sunxsaturn/Fenrir-Dots)
- System installation and exact component pins: [Fenrir Arch](https://github.com/sunxsaturn/Fenrir-Arch)

To synchronize the combined library, preview first with `fenrir-wallpaper sync-library --dry-run`, then run `fenrir-wallpaper sync-library` from Fenrir Dots. The client discovers active volumes from the registry, validates manifests and image bytes, deduplicates by SHA-256, resumes transfers, preserves attribution and never overwrites or deletes local files.

## External references

- [GitHub repository limits](https://docs.github.com/en/repositories/creating-and-managing-repositories/repository-limits)
- [Wikimedia Commons reuse guidance](https://commons.wikimedia.org/wiki/Commons:Reusing_content_outside_Wikimedia/en)
- [Wikimedia API rate limits](https://www.mediawiki.org/wiki/Wikimedia_APIs/Rate_limits)
