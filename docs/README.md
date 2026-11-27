# Fenrir Wallpaper Library navigation

This repository is the public library hub and Volume 01. The canonical registry is the starting point for all volume-aware clients.

## Start here

- [Library overview and publishing rules](../README.md)
- [Live volume registry](../manifest/volumes.json)
- [Volume 01 manifest](../manifest/index.json)
- [Fenrir ecosystem map](https://github.com/sunxsaturn/Fenrir-Arch/blob/main/docs/PROJECT-MAP.md)
- [Desktop multi-volume sync guide](https://github.com/sunxsaturn/Fenrir-Dots/blob/main/docs/WALLPAPER-LIBRARY.md)
- [Private Catalog documentation](https://github.com/sunxsaturn/Fenrir-Wallpaper-Catalog/blob/main/docs/README.md)

## Registered volumes

Do not infer the current collection from this list. The [live registry](../manifest/volumes.json) is authoritative and includes active state, repository, branch, image root and manifest path.

| Volume | Repository | Purpose |
|---|---|---|
| 01 | [Fenrir-Wallpapers](https://github.com/sunxsaturn/Fenrir-Wallpapers) | Hub and original image volume |
| 02 | [Fenrir-Wallpapers-02](https://github.com/sunxsaturn/Fenrir-Wallpapers-02) | First overflow image volume |
| 03 | [Fenrir-Wallpapers-03](https://github.com/sunxsaturn/Fenrir-Wallpapers-03) | Balanced overflow image volume |

Future numbered volumes must be registered here. Desktop clients must discover them dynamically and must not hard-code this table.

## Repository layout

- `Fenrir Wallpapers/` — image files, grouped by canonical category.
- `manifest/index.json` — committed image metadata, hashes, dimensions, provenance and license attribution.
- `manifest/volumes.json` — hub registry and library-wide policy.
- `manifest/publication-approvals.example.json` — template for private, per-image publication decisions.
- `tools/` — validation and publisher utilities.
- `.github/workflows/` — CI and coordinated, bounded population workflows.

Each numbered image volume uses the same image-root and manifest conventions. The registry, not repository naming patterns, determines which volumes are part of the active library.

## Public publishing lifecycle

1. The private Catalog records discovery, provenance, license evidence, rights decisions and acceptance.
2. Public mirroring requires a separate human publication approval for each asset and provider terms that permit redistribution.
3. The publisher verifies exact source bytes, records attribution and updates the public manifest.
4. The volume importer commits only allowed image formats that pass the quality, palette, hash and storage checks.
5. The hub registry exposes the new volume to desktop clients.

Private Catalog databases, quarantine files and publication approval records must never be committed to these public repositories.

## Local desktop use

With the current Fenrir-Dots release installed:

```bash
fenrir-wallpaper sync-library --dry-run
fenrir-wallpaper sync-library
```

This discovers all active volumes from the registry and synchronizes their committed images into one configured wallpaper directory. The local client verifies each manifest and image and preserves per-file attribution. It is distinct from the private Catalog's local accepted-collection sync.

## Category and manifest conventions

Canonical image folders are the eight themed categories plus `unsorted`. Keep category directory slugs stable across all volumes. Each manifest record must retain at least its relative path, SHA-256, exact byte size and MIME type; source, creator, credit, attribution and license metadata should remain attached to each item.

Read [the publisher instructions](../README.md#publish-accepted-catalog-assets) before adding assets. Public commits are persistent Git history: deleting a file in a later commit does not reclaim the earlier Git objects.
