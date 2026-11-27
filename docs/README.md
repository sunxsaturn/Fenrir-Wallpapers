# Fenrir Wallpaper Library navigation

This repository is the public library hub and Volume 01. Use the live volume registry to determine which image repositories are active and how new acquisitions are coordinated.

## Start here

- [Live registry](../manifest/volumes.json) — canonical volume list, active state, acquisition state, storage policy and balancing rules.
- [Hub README](../README.md) — publishing rules, volume roles, storage limits and desktop use.
- [Volume 01 manifest](../manifest/index.json) — image records for this repository.
- [Fenrir Dots multi-volume sync guide](https://github.com/sunxsaturn/Fenrir-Dots/blob/main/docs/WALLPAPER-LIBRARY.md) — local preview and sync workflow.
- [Fenrir project map](https://github.com/sunxsaturn/Fenrir-Arch/blob/main/docs/PROJECT-MAP.md) — relationship to installer, desktop and private Catalog.

## Current registered image volumes

| Volume | Repository | Role from the live registry |
|---|---|---|
| 01 | [Fenrir-Wallpapers](https://github.com/sunxsaturn/Fenrir-Wallpapers) | Hub and first image volume; archived from new acquisition |
| 02 | [Fenrir-Wallpapers-02](https://github.com/sunxsaturn/Fenrir-Wallpapers-02) | Final-fill image volume |
| 03 | [Fenrir-Wallpapers-03](https://github.com/sunxsaturn/Fenrir-Wallpapers-03) | Balanced overflow image volume |

This table is navigation, not a substitute for the registry. Volume status, active state and acquisition eligibility can change independently. Clients must not infer active volumes from repository names or hard-code totals.

## Repository layout

- `manifest/volumes.json` — canonical hub registry and library-wide policy.
- `manifest/index.json` — Volume 01 image manifest.
- `Fenrir Wallpapers/` — committed image bytes.
- `tools/` — publisher and importer utilities.
- `docs/` — project, source and desktop integration guidance.

Each numbered volume keeps its own `manifest/index.json` and image tree. The hub registry determines which volumes are part of the combined collection.

## Publishing lifecycle

1. Private Catalog candidate discovery and rights review.
2. Per-asset acquisition authorization and controlled quarantine.
3. Technical validation, duplicate review and explicit Catalog acceptance.
4. Separate per-asset public-publication approval with compatible license and provider terms.
5. Publisher validates exact bytes and metadata, then writes images and manifest to a selected volume.
6. The hub registry exposes the volume to desktop clients.

A local Catalog acceptance is not a public publication decision.

## Local desktop use

With Fenrir Dots installed, preview and synchronize all active registered volumes:

```bash
fenrir-wallpaper sync-library --dry-run
fenrir-wallpaper sync-library
```

The desktop consumer validates the registry and each manifest before transfer, verifies downloaded bytes, preserves attribution and uses one configured wallpaper directory. This public mirror is separate from private Catalog collection sync.

## Immutable history and source coordination

Public Git history retains previously committed image bytes. Removing a file later does not reclaim those historical objects. Review storage ceilings and the shared balancing plan in the registry before scheduling new imports.

Volume 02 and Volume 03 workflows check the other repository's Actions runs before downloading, keeping the Wikimedia acquisition coordinator serialized. Their scheduled windows and hard storage ceilings are recorded in the registry.
