"""Composite (Layer 3): stand the ORIGINAL product pixels on a styled set.

Never regenerates or grades the product (invariant I1); uniform scale only (no warp).
Adds the grounding cues that make a shot read as a real set: a soft cast shadow, a contact
shadow at the base, and a faded floor reflection on glossy surfaces.

Contract: architecture/04_composite.md
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from tools.lib import imaging as im
from tools.lib import textures as tx
from tools.lib.errors import JobFailed
from tools.lib.scenes import TOP_MARGIN


def build_product_layer(product_rgba: str | Path, canvas: dict, scene: dict) -> Image.Image:
    """Trim + uniformly scale the product for this scene, honouring the top margin."""
    prod = im.trim_alpha(Image.open(product_rgba).convert("RGBA"))
    if prod.width == 0 or prod.height == 0:
        raise JobFailed("composite", "EmptyProduct", "Segmented product is empty.")

    W, H = int(canvas["width"]), int(canvas["height"])
    bottom_y = float(scene["place"]["bottom_y"])
    target_w = int(scene["place"]["width_pct"] * W)
    max_h = max(1, int((bottom_y - TOP_MARGIN) * H))

    scale = min(target_w / prod.width, max_h / prod.height)
    return prod.resize((max(1, round(prod.width * scale)), max(1, round(prod.height * scale))),
                       Image.LANCZOS)


def placement(layer: Image.Image, canvas: dict, scene: dict) -> dict:
    """Where the product sits: horizontally centred, its base on the set's surface."""
    W, H = int(canvas["width"]), int(canvas["height"])
    base_y = float(scene["place"]["bottom_y"]) * H
    left = (W - layer.width) // 2
    top = int(round(base_y - layer.height))
    return {"left": left, "top": top, "base_y": int(round(base_y)),
            "center": (left + layer.width // 2, top + layer.height // 2)}


def _cast_shadow(layer: Image.Image, scene: dict):
    """Silhouette shadow thrown AWAY from the scene's key light."""
    cfg = scene.get("shadow") or {}
    dx, dy = cfg.get("offset", (0.0, 0.05))
    offset = (int(layer.width * dx), int(layer.height * dy))
    blur = max(14, int(layer.width * 0.07))
    return im.soft_shadow(layer.split()[-1], blur, offset, cfg.get("opacity", 0.22))


def _halo(layer: Image.Image, scene: dict) -> Image.Image | None:
    """Soft back-light bloom around the product, so it separates from the set."""
    cfg = scene.get("halo")
    if not cfg:
        return None
    spread = max(6, int(cfg.get("spread", 0.05) * layer.width))
    alpha = layer.split()[-1].filter(ImageFilter.GaussianBlur(spread))
    alpha = alpha.point(lambda v: min(255, int(v * cfg.get("gain", 1.6))))
    alpha = alpha.point(lambda v: int(v * cfg.get("opacity", 0.16)))
    halo = Image.new("RGBA", layer.size, tuple(cfg.get("color", (255, 244, 226))) + (0,))
    halo.putalpha(alpha)
    return halo


def _ellipse_shadow(w: int, h: int, opacity: float, blur: float) -> Image.Image:
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).ellipse([0, 0, w - 1, h - 1], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(max(2.0, blur)))
    m = m.point(lambda v: int(v * opacity))
    sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sh.putalpha(m)
    return sh


def _ground_shadows(layer: Image.Image, scene: dict, pos: dict) -> list[tuple[Image.Image, tuple[int, int]]]:
    """A wide ambient pool plus a tight contact shadow, both straddling the base line."""
    cfg = scene.get("shadow") or {}
    cx = pos["center"][0]
    base_y = pos["base_y"]
    dx = (cfg.get("offset", (0.0, 0.05)))[0]
    shift = int(layer.width * dx * 0.5)

    amb_w, amb_h = max(16, int(layer.width * 1.8)), max(12, int(layer.height * 0.22))
    ambient = _ellipse_shadow(amb_w, amb_h, cfg.get("ambient", 0.10), amb_h * 0.50)
    amb_xy = (cx - amb_w // 2 + shift, base_y - int(amb_h * 0.42))

    con_w, con_h = max(14, int(layer.width * 1.02)), max(10, int(layer.height * 0.13))
    contact = _ellipse_shadow(con_w, con_h, cfg.get("contact", 0.34), con_h * 0.34)
    con_xy = (cx - con_w // 2 + shift, base_y - int(con_h * 0.40))

    return [(ambient, amb_xy), (contact, con_xy)]


def _reflection(layer: Image.Image, scene: dict) -> Image.Image | None:
    cfg = scene.get("reflection")
    if not cfg:
        return None
    depth = max(8, int(cfg.get("depth_pct", 0.24) * layer.height))
    mirrored = layer.transpose(Image.FLIP_TOP_BOTTOM).crop((0, 0, layer.width, depth))

    fade = tx.reflection_fade((layer.width, depth), depth, cfg.get("opacity", 0.18))
    alpha = np.asarray(mirrored.split()[-1], np.float32) * fade[:, None]
    mirrored.putalpha(Image.fromarray(np.clip(alpha, 0, 255).astype(np.uint8)))

    blur = max(1, int(cfg.get("blur_pct", 0.008) * layer.width))
    return mirrored.filter(ImageFilter.GaussianBlur(blur))


def composite(background_path: str | Path, product_layer: Image.Image,
              canvas: dict, scene: dict) -> tuple[Image.Image, dict]:
    """Composite one scene. Returns (RGB at exact canvas size, placement info)."""
    W, H = int(canvas["width"]), int(canvas["height"])
    base = im.fit_cover(Image.open(background_path).convert("RGB"), (W, H)).convert("RGBA")

    pos = placement(product_layer, canvas, scene)
    layer = product_layer

    # 1. silhouette shadow behind the product
    shadow, pad = _cast_shadow(layer, scene)
    base = im.paste_blend(base, shadow, (pos["left"] - pad, pos["top"] - pad))

    # 2. ambient pool + contact shadow, straddling the base line so the product sits on the set
    for ellipse, xy in _ground_shadows(layer, scene, pos):
        base = im.paste_blend(base, ellipse, xy)

    # 3. floor reflection (glossy surfaces only) — drawn under the product
    refl = _reflection(layer, scene)
    if refl is not None:
        base = im.paste_blend(base, refl, (pos["left"], pos["base_y"]))

    # 4. back-light bloom so the product separates from the set
    halo = _halo(layer, scene)
    if halo is not None:
        base = im.paste_blend(base, halo, (pos["left"], pos["top"]))

    # 5. the product itself, from its ORIGINAL pixels
    base = im.paste_blend(base, layer, (pos["left"], pos["top"]))

    return base.convert("RGB"), pos
