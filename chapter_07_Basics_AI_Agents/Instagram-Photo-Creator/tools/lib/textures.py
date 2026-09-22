"""Procedural texture + lighting primitives for luxury backdrops.

Deterministic: every function is seeded and returns the same pixels for the same inputs.
Everything runs in float32 numpy. Textures are synthesised at half resolution and upscaled
(their content is low-frequency, so this is both faster and more natural-looking); fine grain
is added at full resolution by the compositor.
"""
from __future__ import annotations

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

WORK_SCALE = 0.5


# ---------------------------------------------------------------- helpers

def half(size: tuple[int, int]) -> tuple[int, int]:
    return (max(8, int(size[0] * WORK_SCALE)), max(8, int(size[1] * WORK_SCALE)))


def to_img(arr: np.ndarray) -> Image.Image:
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def grid(size: tuple[int, int]) -> tuple[np.ndarray, np.ndarray]:
    """`size` is (width, height) — PIL convention. Returns (xx, yy) each shaped (h, w)."""
    w, h = size
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    return xx, yy


def smoothstep(x: np.ndarray, e0: float, e1: float) -> np.ndarray:
    t = np.clip((x - e0) / max(e1 - e0, 1e-6), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def tint(field: np.ndarray, c_dark, c_light) -> np.ndarray:
    """Map a [0,1] field onto a colour ramp."""
    t = np.clip(field, 0.0, 1.0)[:, :, None]
    a = np.asarray(c_dark, np.float32)[None, None, :]
    b = np.asarray(c_light, np.float32)[None, None, :]
    return a + (b - a) * t


def multiply(img: Image.Image, m: np.ndarray) -> Image.Image:
    return to_img(np.asarray(img, np.float32) * np.clip(m, 0, 2)[:, :, None])


def upscale(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    return img.resize(size, Image.LANCZOS) if img.size != size else img


# ---------------------------------------------------------------- noise

def value_noise(size: tuple[int, int], freq: float, seed: int) -> np.ndarray:
    """Smooth value noise: a small random grid upsampled bicubically."""
    w, h = size
    rng = np.random.default_rng(seed)
    gh, gw = max(2, int(freq)), max(2, int(freq * w / h))
    grid_arr = (rng.random((gh, gw)) * 255).astype(np.uint8)
    up = Image.fromarray(grid_arr).resize((w, h), Image.BICUBIC)
    return np.asarray(up, dtype=np.float32) / 255.0


def fbm(size: tuple[int, int], octaves: int, seed: int, persistence: float = 0.55,
        lacunarity: float = 2.0, base_freq: float = 3.0) -> np.ndarray:
    """Fractal noise, shaped (h, w). `size` is (width, height)."""
    w, h = size
    total = np.zeros((h, w), np.float32)
    amp, norm, freq = 1.0, 0.0, base_freq
    for o in range(octaves):
        total += amp * value_noise(size, freq, seed + o * 977)
        norm += amp
        amp *= persistence
        freq *= lacunarity
    return total / max(norm, 1e-6)


# ---------------------------------------------------------------- materials

def marble(size: tuple[int, int], base, vein, seed: int, scale: float = 13.0,
           turbulence: float = 2.6, sharpness: float = 7.5) -> Image.Image:
    """Polished stone: two crossing vein families warped by turbulence."""
    hw = half(size)
    w, h = hw
    xx, yy = grid(hw)
    tur = fbm(hw, 6, seed, base_freq=2.5)

    p1 = (xx * 0.62 + yy * 0.34) / w * scale + tur * turbulence
    p2 = (xx * -0.28 + yy * 0.72) / h * (scale * 0.55) + tur * (turbulence * 1.5)
    v = np.minimum(np.abs(np.sin(p1 * np.pi)), np.abs(np.sin(p2 * np.pi)))

    veins = np.clip(1.0 - v * sharpness, 0.0, 1.0) ** 1.4
    # two fbm washes at different scales so the stone never reads as a repeating pattern
    wash = smoothstep(fbm(hw, 4, seed + 31, base_freq=1.0), 0.30, 0.78) * 0.55
    blotch = (fbm(hw, 3, seed + 71, base_freq=0.6) - 0.5) * 0.16
    field = np.clip(1.0 - veins * 0.85 - wash + blotch, 0.0, 1.0)

    return upscale(to_img(tint(field, vein, base)), size)


def strata(size: tuple[int, int], base, dark, seed: int, bands: float = 8.0,
           strength: float = 0.30) -> Image.Image:
    """Travertine / limestone: soft horizontal bedding bands + pitting."""
    hw = half(size)
    _, yy = grid(hw)
    n = fbm(hw, 5, seed, base_freq=2.0)
    phase = yy / hw[1] * bands + n * 0.9
    s = np.abs(np.sin(phase * np.pi))
    field = np.clip(1.0 - strength * s, 0.0, 1.0) * (0.94 + 0.12 * n)
    return upscale(to_img(tint(np.clip(field, 0, 1), dark, base)), size)


def plaster(size: tuple[int, int], base, shade, seed: int, mottle: float = 0.45) -> Image.Image:
    """Lime-washed wall: broad mottling, almost no pattern."""
    hw = half(size)
    n = fbm(hw, 6, seed, base_freq=1.8, persistence=0.6)
    fine = fbm(hw, 3, seed + 17, base_freq=14.0)
    field = np.clip(0.55 + (n - 0.5) * 1.5 * mottle + (fine - 0.5) * 0.12, 0, 1)
    return upscale(to_img(tint(field, shade, base)), size)


def velvet(size: tuple[int, int], base, sheen, seed: int, folds: float = 7.0,
           fold_power: float = 1.7) -> Image.Image:
    """Draped velvet: vertical folds catching a raking light."""
    hw = half(size)
    w, h = hw
    xx, _ = grid(hw)
    wobble = fbm(hw, 3, seed, base_freq=1.6)
    phase = xx / w * folds * np.pi + (wobble - 0.5) * 3.2
    fold = (np.sin(phase) * 0.5 + 0.5) ** fold_power
    field = 0.18 + 0.82 * fold
    return upscale(to_img(tint(field, base, sheen)), size)


def wood(size: tuple[int, int], base, dark, seed: int, grain: float = 60.0) -> Image.Image:
    """Sawn oak: fine grain lines plus a few cathedrals."""
    hw = half(size)
    w, h = hw
    _, yy = grid(hw)
    n = fbm(hw, 5, seed, base_freq=2.2)
    phase = yy / h * grain + n * 1.8
    g = np.abs(np.sin(phase * np.pi))
    field = np.clip(1.0 - 0.32 * np.clip(1.0 - g, 0, 1) ** 0.4, 0, 1)
    plank = smoothstep(n, 0.42, 0.58) * 0.07
    field = np.clip(field - plank, 0, 1)
    return upscale(to_img(tint(field, dark, base)), size)


# ---------------------------------------------------------------- light & atmosphere

def linear_light(size: tuple[int, int], angle_deg: float, strength: float,
                 warm=(255, 244, 226)) -> Image.Image:
    """Directional wash of light across the frame."""
    hw = half(size)
    w, h = hw
    xx, yy = grid(hw)
    a = np.deg2rad(angle_deg)
    proj = xx * np.cos(a) + yy * np.sin(a)
    proj = (proj - proj.min()) / max(float(proj.max() - proj.min()), 1e-6)
    rng = np.linspace(1.0, 0.0, w, dtype=np.float32)[None, :]
    ramp = 0.5 * (proj + rng)
    field = smoothstep(ramp, 0.25, 0.95) * (strength / 255.0)
    layer = upscale(to_img(tint(field, (0, 0, 0), warm)), size)
    return layer


def glow(size: tuple[int, int], center: tuple[float, float], radius: float,
         strength: int, color=(255, 250, 240)) -> Image.Image:
    """Soft radial light pool."""
    hw = half(size)
    w, h = hw
    xx, yy = grid(hw)
    cx, cy = center[0] * w, center[1] * h
    dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / max(radius * WORK_SCALE, 1.0)
    falloff = np.clip(1.0 - dist, 0.0, 1.0) ** 2
    field = falloff * (strength / 255.0)
    return upscale(to_img(tint(field, (0, 0, 0), color)), size)


def dapple(size: tuple[int, int], seed: int, blobs: int = 26, strength: float = 0.30,
           blur: float = 46.0) -> np.ndarray:
    """Leaf-shadow dapple. Returns a multiply mask (1 = untouched, <1 = shaded)."""
    hw = half(size)
    layer = Image.new("L", hw, 0)
    draw = ImageDraw.Draw(layer)
    rng = np.random.default_rng(seed)
    for _ in range(blobs):
        r = int(rng.integers(int(28 * WORK_SCALE), int(190 * WORK_SCALE)))
        x = int(rng.integers(-r, hw[0] + r))
        y = int(rng.integers(-r, hw[1] + r))
        draw.ellipse([x - r, y - r, x + r, y + r], fill=int(rng.integers(120, 255)))
    layer = layer.filter(ImageFilter.GaussianBlur(blur * WORK_SCALE))
    m = np.asarray(upscale(layer, size), np.float32) / 255.0
    return 1.0 - strength * m


def blind_shadow(size: tuple[int, int], angle_deg: float, period: float, strength: float,
                 blur: float = 10.0) -> np.ndarray:
    """Venetian-blind stripes as a multiply mask."""
    hw = half(size)
    xx, yy = grid(hw)
    a = np.deg2rad(angle_deg)
    proj = xx * np.cos(a) + yy * np.sin(a)
    s = np.sin(proj / max(period * WORK_SCALE, 1.0) * 2.0 * np.pi)
    m = np.clip(s * 0.5 + 0.5, 0.0, 1.0) ** 1.4
    mask_img = Image.fromarray((m * 255).astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(blur * WORK_SCALE))
    m = np.asarray(upscale(mask_img, size), np.float32) / 255.0
    return 1.0 - strength * m


def bokeh(size: tuple[int, int], seed: int, count: int = 22, radius=(30, 120),
          colors=((126, 152, 104),), strength: float = 0.5, blur: float = 34.0) -> Image.Image:
    """Defocused highlights/highlights-of-foliage, screened over the base."""
    hw = half(size)
    layer = Image.new("RGB", hw, (0, 0, 0))
    draw = ImageDraw.Draw(layer)
    rng = np.random.default_rng(seed)
    for _ in range(count):
        r = int(rng.integers(int(radius[0] * WORK_SCALE), int(radius[1] * WORK_SCALE)))
        x = int(rng.integers(-r, hw[0] + r))
        y = int(rng.integers(-r, hw[1] + r))
        col = colors[int(rng.integers(0, len(colors)))]
        alpha = float(rng.uniform(0.35, 1.0)) * strength
        draw.ellipse([x - r, y - r, x + r, y + r],
                     fill=tuple(int(c * alpha) for c in col))
    layer = layer.filter(ImageFilter.GaussianBlur(blur * WORK_SCALE))
    return upscale(layer, size)


def arch_niche(size: tuple[int, int], center_x: float, top: float, bottom: float,
               width: float, shade: float = 0.90, rim: float = 0.06) -> np.ndarray:
    """A rounded-top arch recess as a multiply mask, with a soft inner rim light."""
    hw = half(size)
    w, h = hw
    cx, half_w = center_x * w, width * w / 2.0
    top_px, bot_px = top * h, bottom * h

    mask = Image.new("L", hw, 0)
    d = ImageDraw.Draw(mask)
    d.rectangle([cx - half_w, top_px + half_w, cx + half_w, bot_px], fill=255)
    d.ellipse([cx - half_w, top_px, cx + half_w, top_px + 2 * half_w], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(6 * WORK_SCALE))
    m = np.asarray(upscale(mask, size), np.float32) / 255.0

    edge = np.asarray(upscale(
        mask.filter(ImageFilter.GaussianBlur(26 * WORK_SCALE)), size), np.float32) / 255.0
    inner_shadow = np.clip(m - edge, 0, 1)
    # 1.0 outside the niche, `shade` inside it, with a soft rim where the two meet
    return 1.0 - m * (1.0 - shade) + inner_shadow * rim


# ---------------------------------------------------------------- cove / floor

def cove_floor_light(size: tuple[int, int], horizon_y: float, floor_drop: float,
                     cove: float = 0.018, sheen: float = 0.0) -> np.ndarray:
    """Darken the floor below the horizon, with a soft cove break at the wall."""
    w, h = size
    yy = np.mgrid[0:h, 0:w][0].astype(np.float32)
    t = smoothstep(yy, horizon_y * h - cove * h, horizon_y * h + cove * h)
    floor = t * (1.0 - floor_drop) + (1.0 - t) * 1.0
    if sheen:
        # a bright band just below the cove where a light pool spills onto the floor
        band = np.exp(-((yy - (horizon_y * h + 0.05 * h)) ** 2) / (2 * (0.035 * h) ** 2))
        floor = floor + sheen * band
    return floor


def reflection_fade(size: tuple[int, int], height: int, top_alpha: float,
                    power: float = 1.6) -> np.ndarray:
    """Alpha ramp for a floor reflection: strongest at the contact line."""
    t = np.linspace(0.0, 1.0, max(2, height), dtype=np.float32)
    return (top_alpha * (1.0 - t) ** power).astype(np.float32)
