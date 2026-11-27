# Fenrir Wallpapers — public gallery hub

**Library generation:** 2 · **State:** population scaffold · **Target:** 5,000 images

This repository owns the public volume registry and stores Volume 01. Volumes 02 and 03 are separate gallery-only repositories. Fenrir-Arch and Fenrir-Dots are software repositories and must never store wallpaper image bytes.

## New gallery contract

- 5,000 unique images in eleven exactly balanced categories.
- Six categories contain 455 images and five contain 454 images.
- Only independently verified CC0 or Public Domain assets with compatible source terms and explicit publication approval are eligible.
- New images must not match any of the 1,871 SHA-256 hashes from the previous public collection.
- Landscape minimum 2560×1440; 3840×2160 preferred.
- Exclude yellow, brown, orange and pink dominant palettes; allow green; prioritize blue, red, purple, violet and black.
- Store image files under `images/<category-slug>/<sha256>.<extension>`. The manifest is authoritative.
- Keep attribution and source evidence even for CC0/Public Domain items.

## Publishing

The private Fenrir Wallpaper Catalog performs discovery, source-term assessment, per-asset rights review, acquisition, image validation, deduplication and human acceptance. Public publication is a separate action requiring a compatible license/provider policy and explicit publication approval.

No image bytes may be committed here merely because they are discoverable or locally accepted. Unknown or conflicting rights are excluded.

## Installation

The completed Fenrir one-command installer reads `manifest/volumes.json`, validates every active volume manifest and downloads all manifest-listed images with SHA-256 and decoded-image verification. There will be no separate wallpaper-pack downloader.

**Population is not complete yet.** Empty manifests are intentional; this repository does not claim that 5,000 images have already been acquired.
