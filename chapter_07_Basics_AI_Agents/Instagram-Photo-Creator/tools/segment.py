"""Segment (Layer 3): cut the product out with a real alpha mask.

Primary: rembg (isnet-general-use). Fallback: Lab colour-distance threshold + largest
connected component (numpy/scikit-image/scipy). Original RGB pixels are preserved.

Contract: architecture/02_segment.md
"""
from __future__ import annotations

import os
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

from config import BASE_DIR
from tools.lib import imaging as im
from tools.lib.errors import JobFailed
from tools.lib.imaging import load_rgb

# keep downloaded ONNX weights inside the project (not the user's home)
os.environ.setdefault("U2NET_HOME", str(BASE_DIR / ".tmp" / "models"))

MIN_COVERAGE = 0.005  # 0.5% of frame

_session = None


def _get_session():
    global _session
    if _session is None:
        from rembg import new_session
        _session = new_session("isnet-general-use")
    return _session


def _rembg_mask(rgb: Image.Image) -> Image.Image:
    from rembg import remove
    cut = remove(rgb, session=_get_session())
    return cut.split()[-1]


def _largest_component(mask: np.ndarray) -> np.ndarray:
    from skimage import measure, morphology
    filled = morphology.remove_small_holes(mask.astype(bool), area_threshold=4096)
    filled = morphology.remove_small_objects(filled, min_size=4096)
    labels = measure.label(filled)
    if labels.max() == 0:
        return filled
    counts = np.bincount(labels.ravel())
    counts[0] = 0
    return labels == counts.argmax()


def _threshold_mask(rgb: Image.Image) -> Image.Image:
    from skimage.color import rgb2lab

    arr = np.asarray(rgb, dtype=np.float32) / 255.0
    lab = rgb2lab(arr)
    h, w = lab.shape[:2]
    patch = max(8, min(h, w) // 20)
    corners = np.concatenate([
        lab[:patch, :patch].reshape(-1, 3),
        lab[:patch, -patch:].reshape(-1, 3),
        lab[-patch:, :patch].reshape(-1, 3),
        lab[-patch:, -patch:].reshape(-1, 3),
    ])
    bg = np.median(corners, axis=0)
    dist = np.sqrt(((lab - bg) ** 2).sum(axis=2))
    mask = dist > 12.0
    mask = _largest_component(mask)
    return Image.fromarray((mask * 255).astype(np.uint8), "L")


def segment(source_path: str | Path, job_dir: str | Path) -> dict:
    job_dir = Path(job_dir)
    job_dir.mkdir(parents=True, exist_ok=True)
    rgb = load_rgb(source_path)

    method = "rembg"
    try:
        mask = _rembg_mask(rgb)
    except Exception:  # noqa: BLE001 - any model/runtime failure falls back
        method = "threshold"
        mask = _threshold_mask(rgb)

    mask = mask.convert("L").filter(ImageFilter.GaussianBlur(1.0))

    coverage = float((np.asarray(mask) > 128).mean())
    if coverage < MIN_COVERAGE:
        raise JobFailed("segment", "MaskEmpty",
                        "Could not isolate the product (mask nearly empty). "
                        "Try a clearer photo with the product on a plain background.")

    rgba = rgb.convert("RGBA")
    rgba.putalpha(mask)
    rgba = im.decontaminate_edges(rgba)

    rgba_path = job_dir / "product_rgba.png"
    mask_path = job_dir / "mask.png"
    rgba.save(rgba_path)
    mask.save(mask_path)

    return {
        "product_rgba": str(rgba_path),
        "mask": str(mask_path),
        "coverage": coverage,
        "method": method,
    }
