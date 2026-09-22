"""Pillow/numpy primitives shared by the composer tools. No I/O side effects beyond loads."""
from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_rgb(path: str | Path) -> Image.Image:
    return Image.open(path).convert("RGB")


def ensure_rgb(img: Image.Image) -> Image.Image:
    if img.mode == "RGB":
        return img
    if img.mode in ("RGBA", "LA", "P"):
        rgba = img.convert("RGBA")
        bg = Image.new("RGB", rgba.size, (255, 255, 255))
        bg.paste(rgba, mask=rgba.split()[-1])
        return bg
    return img.convert("RGB")


def fit_cover(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    """Cover-scale then center-crop. Never stretches (invariant I4)."""
    tw, th = size
    scale = max(tw / img.width, th / img.height)
    nw, nh = max(1, round(img.width * scale)), max(1, round(img.height * scale))
    resized = img.resize((nw, nh), Image.LANCZOS)
    left, top = (nw - tw) // 2, (nh - th) // 2
    return resized.crop((left, top, left + tw, top + th))


def screen(base: Image.Image, light: Image.Image) -> Image.Image:
    b = np.asarray(base, dtype=np.float32) / 255.0
    l = np.asarray(light, dtype=np.float32) / 255.0
    out = 1.0 - (1.0 - b) * (1.0 - l)
    return Image.fromarray((out * 255.0).astype(np.uint8))


def vignette(img: Image.Image, strength: float = 0.30) -> Image.Image:
    w, h = img.size
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    cx, cy = w / 2.0, h / 2.0
    dist = np.sqrt(((xx - cx) / cx) ** 2 + ((yy - cy) / cy) ** 2)
    mask = np.clip(1.0 - strength * np.clip(dist - 0.35, 0, None) ** 1.6, 0.0, 1.0)
    arr = np.asarray(img, dtype=np.float32) * mask[:, :, None]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def grain(img: Image.Image, seed: int, amplitude: float = 3.0) -> Image.Image:
    rng = np.random.default_rng(seed)
    arr = np.asarray(img, dtype=np.float32)
    noise = rng.normal(0.0, amplitude, arr.shape[:2]).astype(np.float32)[:, :, None]
    return Image.fromarray(np.clip(arr + noise, 0, 255).astype(np.uint8))


def soft_shadow(alpha: Image.Image, blur_radius: int, offset: tuple[int, int],
                opacity: float, color: tuple[int, int, int] = (0, 0, 0)
                ) -> tuple[Image.Image, int]:
    """Blurred RGBA drop shadow from an L-mode alpha channel.

    Returns (shadow, pad) — `pad` is the padding added around the source, so the caller can
    align the shadow's product with the real product position.
    """
    w, h = alpha.size
    pad = blur_radius * 2 + max(abs(offset[0]), abs(offset[1])) + 4
    canvas = Image.new("L", (w + 2 * pad, h + 2 * pad), 0)
    canvas.paste(alpha, (pad + offset[0], pad + offset[1]))
    canvas = canvas.filter(ImageFilter.GaussianBlur(blur_radius))
    canvas = canvas.point(lambda v: int(v * opacity))
    shadow = Image.new("RGBA", canvas.size, color + (0,))
    shadow.putalpha(canvas)
    return shadow, pad


def paste_blend(base: Image.Image, overlay: Image.Image,
                xy: tuple[int, int]) -> Image.Image:
    """Alpha-composite `overlay` at `xy`, clipping anything that falls off the canvas."""
    if base.mode != "RGBA":
        base = base.convert("RGBA")
    x, y = int(round(xy[0])), int(round(xy[1]))
    bw, bh = base.size
    ox0, oy0 = max(0, -x), max(0, -y)
    ox1, oy1 = min(overlay.width, bw - x), min(overlay.height, bh - y)
    if ox1 <= ox0 or oy1 <= oy0:
        return base
    base.alpha_composite(overlay.crop((ox0, oy0, ox1, oy1)), (x + ox0, y + oy0))
    return base


def decontaminate_edges(img: Image.Image, sigma: float | None = None) -> Image.Image:
    """Replace colour in the semi-transparent fringe with nearby solid product colour.

    A soft alpha matte keeps the ORIGINAL backdrop's colour in its feathered edge. Composited
    onto a very different set (a pale product on deep velvet) that reads as a bright halo.
    Only the fringe (alpha < 220) is touched; solid product pixels are byte-identical.
    """
    from scipy.ndimage import gaussian_filter

    arr = np.asarray(img.convert("RGBA"), np.float32)
    rgb, alpha = arr[..., :3], arr[..., 3]
    s = float(sigma or max(2.0, min(img.size) * 0.006))

    core = (alpha > 220).astype(np.float32)
    den = gaussian_filter(core, s)
    has_core = den > 1e-3

    avg = np.empty_like(rgb)
    for i in range(3):
        num = gaussian_filter(rgb[..., i] * core, s)
        avg[..., i] = np.where(has_core, num / np.maximum(den, 1e-6), rgb[..., i])

    weight = np.clip(1.0 - alpha / 220.0, 0.0, 1.0)[..., None]
    out_rgb = rgb * (1.0 - weight) + avg * weight
    out = np.concatenate([out_rgb, alpha[..., None]], axis=-1)
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA")


def trim_alpha(img: Image.Image) -> Image.Image:
    """Crop an RGBA image to its non-transparent bounding box."""
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    bbox = img.split()[-1].getbbox()
    return img.crop(bbox) if bbox else img

