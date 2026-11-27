# Public wallpaper population — closed

**Status:** closed on 2026-11-27  
**Mode:** existing assets only  
**Fixed wallpaper-count target:** none

## Published inventory

The public Fenrir wallpaper library contains 1,871 image records in three registered volumes. The 2026-11-27 audit of the recursive repository trees found 1,871 content-hash filenames and no cross-volume duplicate filenames; manifests report the same inventory.

| Volume | Repository | Images | Desktop sync | Acquisition |
|---|---|---:|---|---|
| 01 | `sunxsaturn/Fenrir-Wallpapers` | 134 | Active | Closed |
| 02 | `sunxsaturn/Fenrir-Wallpapers-02` | 1,132 | Active | Closed |
| 03 | `sunxsaturn/Fenrir-Wallpapers-03` | 605 | Active | Closed |

## Category snapshot

| Category | Images |
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

This is the actual distribution, not a goal. It is not a reason to find, acquire or move additional images. The existing category folders are retained as committed.

## What closure means

- All existing manifest-listed images remain published and eligible for desktop synchronization.
- Volume 02 and Volume 03 acquisition workflows have been removed.
- Every volume remains active for sync and is set to acquisition disabled and status closed.
- No scheduled or manual population workflow is part of the public-library operating plan.
- No new volume is planned.
- No image is deleted, overwritten, moved or duplicated to rebalance the categories.
- Rights, license, source and attribution metadata remain part of every public image record.

## Audit and desktop sync

From Fenrir Dots:

```bash
fenrir-wallpaper audit-library --json
fenrir-wallpaper sync-library --dry-run
```

The audit reads the registry and committed manifests only. It validates content-hash declarations, uniqueness, metadata and category counts without downloading image bytes or inspecting the local wallpaper folder. The local sync preview checks which public images are missing. A separately confirmed `fenrir-wallpaper sync-library` downloads only already-published manifest entries and verifies downloaded image bytes before installation.

The local Catalog is a separate workflow. Its desktop sync similarly copies only already accepted assets and does not create new rights decisions or acquire provider images.

The hub registry manifest/volumes.json is authoritative for the current closed state. This document is a dated explanation of the closure snapshot.
