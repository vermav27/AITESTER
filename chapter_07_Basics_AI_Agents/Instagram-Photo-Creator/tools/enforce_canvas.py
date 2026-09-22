"""Enforce canvas (Layer 3): guarantee the exact 9:16 4K frame.

Contract: architecture/05_canvas-watermark.md
"""
from __future__ import annotations

from PIL import Image

from tools.lib import imaging as im
from tools.lib.errors import JobFailed


def enforce_canvas(img: Image.Image, canvas: dict) -> Image.Image:
    W, H = int(canvas["width"]), int(canvas["height"])
    if img.size == (W, H):
        return img.convert("RGB")
    out = im.fit_cover(img.convert("RGB"), (W, H))
    if out.size != (W, H):
        raise JobFailed("canvas", "CanvasMismatch",
                        f"Expected {W}x{H}, got {out.size}.")
    return out
