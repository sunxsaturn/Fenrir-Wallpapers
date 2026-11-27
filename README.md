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
| 01 | [Fenrir-Wallpapers](https://github.com/sunxsaturn/Fenrir-Wallpapers) | Hub and first image volume | Archived; no new acquisition |
| 02 | [Fenrir-Wallpapers-02](https://github.com/sunxsaturn/Fenrir-Wallpapers-02) | Final-fill image volume | Guarded final-fill windows |
| 03 | [Fenrir-Wallpapers-03](https://github.com/sunxsaturn/Fenrir-Wallpapers-03) | Balanced overflow image volume | Guarded balanced population |

All three are active for desktop synchronization. The registry's `active` field controls what clients sync; `acquisition_enabled` and `status` describe publisher workflow state. Do not infer one from the other.

The manifests in the volume repositories are authoritative for image records and current counts. The hub registry is authoritative for repository discovery and shared policy. Desktop clients must read the registry instead of hard-coding volume names or counts.

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

## Storage and immutable history

- Volume 01 retains its original conservative 900 MiB Git-object budget and is archived.
- New numbered volumes target 8 GiB of Git-object storage each, subject to the hard repository ceiling and shared library policy.
- New images are capped at 45 MiB; upload batches remain bounded below GitHub's push limits.
- Image counts and category balance are measured from the live manifests. The balancing policy uses the current largest global category count and available shared capacity; it is not a fixed historical count.
- Git history is persistent. Deleting a file in a later commit does not reclaim the original Git objects. Do not repeatedly replace or recompress committed images.

The [live registry](manifest/volumes.json) contains the current storage policy, active roles, publisher coordination windows and shared balancing rules. Read it before changing acquisition workflows.

## Coordinated population

The active acquisition workflows are guarded so Volume 02 and Volume 03 do not run Wikimedia population concurrently. Each workflow checks the other public repository's Actions runs before starting; the registry records the scheduled windows and role of each volume.

This coordination protects a single serialized source-acquisition policy. Splitting images across GitHub repositories does not change provider rights or request limits.

## Fenrir integration

- Private discovery, rights evidence, acquisition and acceptance: [Fenrir Wallpaper Catalog](https://github.com/sunxsaturn/Fenrir-Wallpaper-Catalog)
- Desktop UI, local rotation and multi-volume sync: [Fenrir Dots](https://github.com/sunxsaturn/Fenrir-Dots)
- System installation and exact component pins: [Fenrir Arch](https://github.com/sunxsaturn/Fenrir-Arch)

To synchronize the combined library, preview first with `fenrir-wallpaper sync-library --dry-run`, then run `fenrir-wallpaper sync-library` from Fenrir Dots. The client discovers active volumes from the registry, validates manifests and image bytes, deduplicates by SHA-256, resumes transfers, preserves attribution and never overwrites or deletes local files.

## External references

- [GitHub repository limits](https://docs.github.com/en/repositories/creating-and-managing-repositories/repository-limits)
- [Wikimedia Commons reuse guidance](https://commons.wikimedia.org/wiki/Commons:Reusing_content_outside_Wikimedia/en)
- [Wikimedia API rate limits](https://www.mediawiki.org/wiki/Wikimedia_APIs/Rate_limits)
