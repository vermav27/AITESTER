"""Watermark (Layer 3): stamp one small brand handle on each final image.

Contract: architecture/05_canvas-watermark.md
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

_FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Futura.ttc",
    "/System/Library/Fonts/Supplemental/Avenir Next.ttc",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/Library/Fonts/Arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def _load_font(px: int):
    for path in _FONT_CANDIDATES:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, px)
            except OSError:
                continue
    try:
        return ImageFont.load_default(size=px)  # Pillow >= 10.1
    except TypeError:
        return ImageFont.load_default()


def _measure(text: str, font) -> tuple[int, int, tuple[int, int, int, int]]:
    probe = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    box = probe.textbbox((0, 0), text, font=font)
    return box[2] - box[0], box[3] - box[1], box


def _fit_font(text: str, target_width: int, upper_px: int):
    """Binary-search a font size whose rendered text width ≈ target_width."""
    lo, hi = 8, max(9, upper_px)
    best = _load_font(lo)
    for _ in range(12):
        mid = (lo + hi) // 2
        font = _load_font(mid)
        w, _, _ = _measure(text, font)
        if w <= target_width:
            best, lo = font, mid + 1
        else:
            hi = mid - 1
        if lo > hi:
            break
    return best


def add_watermark(img: Image.Image, handle: str, opacity: float = 0.55,
                  size_pct: float = 0.15, position: str = "bottom-right",
                  margin_pct: float = 0.04) -> tuple[Image.Image, list[int]]:
    """Draw the handle. `size_pct` is the target text WIDTH as a fraction of canvas width.

    Returns (image, bbox) where bbox is the watermark's pixel box.
    """
    base = img.convert("RGBA")
    W, H = base.size
    target_w = int(max(0.03, min(0.35, size_pct)) * W)
    font = _fit_font(handle, target_w, upper_px=int(W * 0.08))

    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    tw, th, bbox = _measure(handle, font)
    margin = int(margin_pct * W)

    if position == "bottom-left":
        x = margin
    elif position == "bottom-center":
        x = (W - tw) // 2
    else:
        x = W - tw - margin
    y = H - th - margin - bbox[1]

    alpha = int(255 * max(0.0, min(1.0, opacity)))
    # faint shadow for legibility on light and dark scenes
    draw.text((x + 2, y + 2), handle, font=font, fill=(0, 0, 0, int(alpha * 0.45)))
    draw.text((x, y), handle, font=font, fill=(255, 255, 255, alpha))

    out = Image.alpha_composite(base, overlay).convert("RGB")
    return out, [x, y, x + tw, y + th]
