"""Ingest (Layer 3): validate + normalize an upload to a clean sRGB PNG.

Contract: architecture/01_input-contract.md
"""
from __future__ import annotations

import shutil
from pathlib import Path

from PIL import Image, ImageOps

from tools.lib.errors import JobFailed
from tools.lib.imaging import sha256_file

ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".webp"}
MAX_BYTES = 15 * 1024 * 1024
MIN_LONG_EDGE = 1000
MIN_LONG_EDGE_HARD = 700  # below this even a warning-level pass is refused


def validate(path: str | Path) -> None:
    p = Path(path)
    if not p.exists():
        raise JobFailed("ingest", "MissingFile", "Uploaded file was not found.")
    if p.suffix.lower() not in ALLOWED_EXT:
        raise JobFailed("ingest", "BadExtension",
                        f"Unsupported file type '{p.suffix}'. Use JPG, PNG or WEBP.")
    size = p.stat().st_size
    if size == 0:
        raise JobFailed("ingest", "EmptyFile", "The uploaded file is empty.")
    if size > MAX_BYTES:
        raise JobFailed("ingest", "InputTooLarge",
                        f"File is {size / 1e6:.1f} MB; limit is 15 MB.")


def ingest(src_path: str | Path, job_dir: str | Path) -> dict:
    src = Path(src_path)
    job_dir = Path(job_dir)
    job_dir.mkdir(parents=True, exist_ok=True)

    validate(src)

    try:
        with Image.open(src) as im:
            im = ImageOps.exif_transpose(im)
            if im.mode in ("RGBA", "LA", "P"):
                rgba = im.convert("RGBA")
                base = Image.new("RGB", rgba.size, (255, 255, 255))
                base.paste(rgba, mask=rgba.split()[-1])
                im = base
            else:
                im = im.convert("RGB")
    except OSError as exc:
        raise JobFailed("ingest", "UnreadableImage", f"Could not decode the image: {exc}") from exc

    long_edge = max(im.size)
    if long_edge < MIN_LONG_EDGE_HARD:
        raise JobFailed("ingest", "InputTooSmall",
                        f"Image long edge is {long_edge}px; need at least {MIN_LONG_EDGE}px for 4K.")

    out = job_dir / "source_srgb.png"
    im.save(out, "PNG")

    # keep an untouched copy beside it for reproducibility
    shutil.copy2(src, job_dir / f"source_original{src.suffix.lower()}")

    return {
        "path": str(out),
        "original": str(job_dir / f"source_original{src.suffix.lower()}"),
        "width": im.width,
        "height": im.height,
        "sha256": sha256_file(out),
        "low_res_warning": long_edge < MIN_LONG_EDGE,
    }
