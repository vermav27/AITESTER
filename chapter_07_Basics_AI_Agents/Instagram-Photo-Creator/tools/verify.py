"""Verify (Layer 3): numeric fidelity gate. Fail closed.

Contract: architecture/06_verify-export.md
"""
from __future__ import annotations

import numpy as np
from PIL import Image

from tools.lib.errors import JobFailed


def _product_region(product_layer: Image.Image, composed_rgb: Image.Image, pos: dict):
    """Crop (source, output, mask) at the product's EXACT placement rect.

    Rounding the centre back into a rectangle can land one pixel off (round-half-to-even), which
    would compare shifted pixels at every edge. The compositor hands us `left`/`top`; use them.
    """
    w, h = product_layer.size
    x, y = int(pos["left"]), int(pos["top"])
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(composed_rgb.width, x + w), min(composed_rgb.height, y + h)
    region = composed_rgb.crop((x0, y0, x1, y1))
    mask_full = product_layer.split()[-1]
    mask = mask_full.crop((x0 - x, y0 - y, x1 - x, y1 - y))
    src = product_layer.convert("RGB").crop((x0 - x, y0 - y, x1 - x, y1 - y))
    return src, region, mask


def product_fidelity(product_layer: Image.Image, composed_rgb: Image.Image,
                     pos: dict) -> dict:
    """ΔE2000 + SSIM over the OPAQUE product core (source pixels vs. composited).

    Only pixels the mask calls fully opaque are compared. A feathered edge pixel is *meant* to
    blend with the backdrop, so including it would measure the background, not the product.
    """
    from skimage.color import deltaE_ciede2000, rgb2lab
    from skimage.metrics import structural_similarity as ssim

    src, out, mask_img = _product_region(product_layer, composed_rgb, pos)
    m = np.asarray(mask_img) >= 250
    if m.sum() < 100:
        return {"deltaE_mean": 0.0, "ssim_masked": 1.0, "pixels": int(m.sum())}

    a = np.asarray(src, dtype=np.float32) / 255.0
    b = np.asarray(out, dtype=np.float32) / 255.0
    de = deltaE_ciede2000(rgb2lab(a), rgb2lab(b))[m].mean()

    # SSIM uses a local window, so a pixel on the rim would average the product against the
    # backdrop showing through its transparent neighbours. Erode first so every window sits
    # wholly inside the product.
    from scipy.ndimage import binary_erosion
    core = binary_erosion(m, iterations=3)
    if core.sum() < 100:
        core = m
    _, s = ssim((a * 255).astype(np.uint8), (b * 255).astype(np.uint8),
                channel_axis=2, data_range=255, full=True)
    return {"deltaE_mean": float(de), "ssim_masked": float(s[core].mean()),
            "pixels": int(m.sum()), "ssim_pixels": int(core.sum())}


def verify(canvas: dict, final_img: Image.Image, product_layer: Image.Image,
           pos: dict, coverage: float, watermark_bbox: list[int],
           max_deltaE: float = 3.0, min_ssim: float = 0.95) -> dict:
    W, H = int(canvas["width"]), int(canvas["height"])
    if final_img.size != (W, H):
        raise JobFailed("verify", "CanvasMismatch",
                        f"Expected {W}x{H}, got {final_img.size}.")
    if coverage < 0.005:
        raise JobFailed("verify", "MaskEmpty", "Product coverage too small.")

    metrics = product_fidelity(product_layer, final_img, pos)
    if metrics["deltaE_mean"] > max_deltaE:
        raise JobFailed("verify", "ColorDrift",
                        f"Product colour drifted (ΔE {metrics['deltaE_mean']:.2f} > {max_deltaE}).")
    if metrics["ssim_masked"] < min_ssim:
        raise JobFailed("verify", "StructureDrift",
                        f"Product structure drifted (SSIM {metrics['ssim_masked']:.3f} < {min_ssim}).")

    if not watermark_bbox or watermark_bbox[2] <= watermark_bbox[0]:
        raise JobFailed("verify", "WatermarkMissing", "Watermark was not applied.")

    return {
        "deltaE_mean": round(metrics["deltaE_mean"], 3),
        "ssim_masked": round(metrics["ssim_masked"], 4),
        "product_pixels": metrics["pixels"],
        "watermark_bbox": watermark_bbox,
        "verdict": "pass",
    }
