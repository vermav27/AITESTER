"""The four styled scenes — a single source of truth for palette, prompt and pixel build.

Each scene is a self-contained set: wall material + floor material + cove, architectural detail,
directional lighting and atmosphere. The product is never drawn here (invariant I2); it is
composited later from its original pixels.

`build(size, seed)` is deterministic: the same seed always yields the same backdrop.
"""
from __future__ import annotations

import numpy as np
from PIL import Image

from tools.lib import textures as tx
from tools.lib.imaging import grain, screen, vignette

# Scenes are all built with the cove (wall/floor break) a little above the product's base, so the
# product reads as standing on the surface with its shadow and reflection landing on the floor.
TOP_MARGIN = 0.09


def _stack(wall: Image.Image, floor: Image.Image, horizon: float,
           cove: float = 0.022) -> Image.Image:
    """Blend a wall into a floor with a soft cyclorama break at `horizon`."""
    w, h = wall.size
    yy = np.mgrid[0:h, 0:w][0].astype(np.float32)
    t = tx.smoothstep(yy, horizon * h - cove * h, horizon * h + cove * h)[:, :, None]
    a = np.asarray(wall, np.float32)
    b = np.asarray(floor, np.float32)
    return tx.to_img(a * (1.0 - t) + b * t)


# ------------------------------------------------------------------ builders

def build_marble(size, seed, spec) -> Image.Image:
    """Polished Calacatta: book-matched stone, glossy floor, raking daylight."""
    wall = tx.marble(size, (245, 240, 233), (196, 184, 170), seed, scale=8.0,
                     turbulence=3.0, sharpness=6.0)
    floor = tx.marble(size, (212, 202, 188), (168, 154, 138), seed + 5, scale=5.5,
                      turbulence=3.6, sharpness=5.0)

    img = _stack(wall, floor, spec["horizon"])
    img = tx.multiply(img, tx.cove_floor_light(size, spec["horizon"], 0.18, sheen=0.10))
    img = screen(img, tx.glow(size, (0.26, 0.16), 1500.0, 62, (255, 250, 240)))
    img = screen(img, tx.linear_light(size, 128.0, 34, (255, 246, 228)))
    return grain(vignette(img, 0.30), seed * 131 + 11, 1.8)


def build_velvet(size, seed, spec) -> Image.Image:
    """Emerald Velvet: draped folds, a single raking light, deep shadow."""
    wall = tx.velvet(size, (12, 40, 34), (66, 116, 96), seed, folds=8.0, fold_power=1.9)
    floor = tx.velvet(size, (30, 68, 58), (68, 108, 90), seed + 3, folds=5.0, fold_power=2.4)

    img = _stack(wall, floor, spec["horizon"])
    img = tx.multiply(img, tx.cove_floor_light(size, spec["horizon"], 0.26))
    img = screen(img, tx.glow(size, (0.80, 0.28), 1250.0, 74, (255, 236, 205)))
    img = screen(img, tx.glow(size, (0.18, 0.10), 900.0, 22, (170, 214, 196)))
    return grain(vignette(img, 0.52), seed * 131 + 23, 2.4)


def build_travertine(size, seed, spec) -> Image.Image:
    """Travertine Atelier: an arched niche, warm bedding stone, afternoon dapple."""
    wall = tx.strata(size, (234, 219, 199), (202, 181, 156), seed, bands=7.0, strength=0.26)
    floor = tx.strata(size, (208, 189, 166), (176, 153, 128), seed + 7, bands=5.0, strength=0.38)

    # architectural niche behind the product
    wall = tx.multiply(wall, tx.arch_niche(size, 0.5, 0.13, spec["horizon"] + 0.015,
                                           width=0.66, shade=0.90, rim=0.07))

    img = _stack(wall, floor, spec["horizon"])
    img = tx.multiply(img, tx.cove_floor_light(size, spec["horizon"], 0.20, sheen=0.07))
    img = tx.multiply(img, tx.blind_shadow(size, 112.0, period=190.0, strength=0.16, blur=26.0))
    img = screen(img, tx.glow(size, (0.70, 0.14), 1400.0, 58, (255, 242, 214)))
    return grain(vignette(img, 0.28), seed * 131 + 37, 2.0)


def build_botanical(size, seed, spec) -> Image.Image:
    """Botanical Salon: sage plaster, oak floor, defocused greenery."""
    wall = tx.plaster(size, (225, 231, 218), (193, 204, 189), seed, mottle=0.5)
    wall = screen(wall, tx.bokeh(size, seed + 11, count=26, radius=(36, 150),
                                 colors=((118, 146, 98), (152, 174, 128), (206, 216, 186)),
                                 strength=0.42, blur=40.0))
    wall = tx.multiply(wall, tx.dapple(size, seed + 19, blobs=24, strength=0.22, blur=52.0))

    floor = tx.wood(size, (208, 174, 128), (163, 126, 86), seed + 4, grain=46.0)

    img = _stack(wall, floor, spec["horizon"])
    img = tx.multiply(img, tx.cove_floor_light(size, spec["horizon"], 0.22, sheen=0.04))
    img = screen(img, tx.glow(size, (0.50, 0.04), 1600.0, 54, (255, 253, 244)))
    return grain(vignette(img, 0.24), seed * 131 + 53, 1.8)


# ------------------------------------------------------------------ registry

SCENES = [
    {
        "id": "marble",
        "name": "Polished Calacatta",
        "blurb": "book-matched marble, glossy floor, raking daylight",
        "accent": "#c9a227",
        "prompt": ("Generate an empty 9:16 vertical luxury product-photography set: a polished "
                   "white Calacatta marble wall meeting a glossy marble floor, a soft raking "
                   "daylight pool from the upper left, gentle reflection on the stone floor. "
                   "No product, no props, no text, no people. Editorial, high-end, minimal."),
        "horizon": 0.70,
        "place": {"width_pct": 0.58, "bottom_y": 0.82},
        "reflection": {"opacity": 0.42, "blur_pct": 0.005, "depth_pct": 0.34},
        "shadow": {"opacity": 0.34, "contact": 0.40, "ambient": 0.14, "offset": (0.045, 0.055)},
        "halo": {"opacity": 0.055, "spread": 0.045, "gain": 1.25, "color": (255, 249, 240)},
        "build": build_marble,
    },
    {
        "id": "velvet",
        "name": "Emerald Velvet",
        "blurb": "draped emerald folds, one raking light, deep shadow",
        "accent": "#3f7a63",
        "prompt": ("Generate an empty 9:16 vertical luxury set: deep emerald green velvet drapery "
                   "falling in soft vertical folds, a single warm raking light from the right, "
                   "dark rich shadows, a velvet surface below. No product, no props, no text. "
                   "Jewellery-campaign mood, moody and expensive."),
        "horizon": 0.74,
        "place": {"width_pct": 0.60, "bottom_y": 0.83},
        "reflection": {"opacity": 0.22, "blur_pct": 0.008, "depth_pct": 0.26},
        "shadow": {"opacity": 0.44, "contact": 0.38, "ambient": 0.14, "offset": (-0.04, 0.055)},
        # the emerald set is already high-contrast: a bloom would read as a cutout
        "halo": None,
        "build": build_velvet,
    },
    {
        "id": "travertine",
        "name": "Travertine Atelier",
        "blurb": "arched stone niche, warm bedding, afternoon dapple",
        "accent": "#b98a5e",
        "prompt": ("Generate an empty 9:16 vertical luxury set: a warm travertine limestone wall "
                   "with a tall arched niche recess, a stone floor, soft diagonal window light "
                   "and a faint blind shadow, warm afternoon tones, subtle stone pitting. "
                   "No product, no props, no text. Architectural, gallery-like, serene."),
        "horizon": 0.72,
        "place": {"width_pct": 0.56, "bottom_y": 0.83},
        "reflection": {"opacity": 0.30, "blur_pct": 0.006, "depth_pct": 0.28},
        "shadow": {"opacity": 0.32, "contact": 0.40, "ambient": 0.14, "offset": (-0.042, 0.055)},
        "halo": {"opacity": 0.07, "spread": 0.05, "gain": 1.25, "color": (255, 241, 216)},
        "build": build_travertine,
    },
    {
        "id": "botanical",
        "name": "Botanical Salon",
        "blurb": "sage plaster, oak floor, defocused greenery",
        "accent": "#7d9471",
        "prompt": ("Generate an empty 9:16 vertical luxury set: a soft sage-green lime-plaster "
                   "wall with gentle mottling and dappled leaf shadows, a warm oak floor, airy "
                   "daylight from above and heavily defocused green foliage bokeh. No product, "
                   "no props, no text. Fresh, calm, natural-luxury."),
        "horizon": 0.74,
        "place": {"width_pct": 0.58, "bottom_y": 0.84},
        "reflection": {"opacity": 0.26, "blur_pct": 0.006, "depth_pct": 0.26},
        "shadow": {"opacity": 0.30, "contact": 0.38, "ambient": 0.13, "offset": (0.0, 0.06)},
        "halo": {"opacity": 0.06, "spread": 0.045, "gain": 1.25, "color": (255, 253, 246)},
        "build": build_botanical,
    },
]

SCENE_IDS = [s["id"] for s in SCENES]


def get_scenes() -> list[dict]:
    return SCENES


def get_scene(scene_id: str) -> dict:
    for s in SCENES:
        if s["id"] == scene_id:
            return s
    raise KeyError(scene_id)


def scenes_public() -> list[dict]:
    """JSON-safe projection for the web layer (the `build` callable must not be serialized)."""
    return [{k: s[k] for k in ("id", "name", "blurb", "accent")} for s in SCENES]


def build_background(scene: dict, size: tuple[int, int], seed: int) -> Image.Image:
    return scene["build"](size, seed, scene)
