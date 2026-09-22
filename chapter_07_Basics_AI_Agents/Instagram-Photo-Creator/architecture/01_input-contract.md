# 01 — Input Contract (`ingest.py`)

## Goal
Turn an arbitrary uploaded file into a validated, sRGB, orientation-correct RGB raster in `.tmp/<job_id>/source_srgb.png`.

## Inputs
- Raw upload bytes (`.jpg/.jpeg/.png/.webp`), filename, declared content-type.
- Max size 15 MB; long edge ≥ 1000 px.

## Logic
1. Reject empty body / disallowed extension / disallowed magic bytes.
2. `PIL.Image.open` → `ImageOps.exif_transpose` (honour camera orientation).
3. Convert to `RGB`; strip alpha by compositing on white.
4. Normalize to sRGB (drop exotic ICC by converting through `ImageCms` when present).
5. Save PNG to `.tmp/<job_id>/source_srgb.png`; record `(w, h, sha256)`.

## Edge cases
| Case | Handling |
|------|----------|
| CMYK / palette image | convert to RGB first |
| Progressive JPEG, no EXIF | pass through |
| Long edge < 1000 px | `JobFailed("InputTooSmall")` — 4K upscale would be fake detail |
| > 15 MB | `JobFailed("InputTooLarge")` |
| Rotated phone photo | EXIF transpose fixes it before anything else |

## Output
`{ "path": "...", "width": w, "height": h, "sha256": "..." }`
