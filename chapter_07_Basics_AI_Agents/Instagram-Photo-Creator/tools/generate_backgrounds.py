"""Generate backgrounds (Layer 3): four EMPTY 9:16 sets, one per scene.

providers:
  local  - deterministic procedural renderer (tools/lib/scenes.py + textures.py): materials,
           architecture, directional light and atmosphere, seeded.
  gemini - text-to-image via the configured image model (needs image quota).
  auto   - probe gemini once; fall back to local if it has no quota.

The product is never drawn here (invariant I2).
Contract: architecture/03_generate-backgrounds.md
"""
from __future__ import annotations

import io
from pathlib import Path

from PIL import Image

from tools import llm_client
from tools.lib import imaging as im
from tools.lib.scenes import build_background, get_scenes


def resolve_provider(mode: str) -> tuple[str, str]:
    """Return (provider, note). Probes Gemini once when mode == 'auto'."""
    mode = (mode or "auto").lower()
    if mode == "local":
        return "local", "forced local"
    if mode == "gemini":
        return "gemini", "forced gemini"
    probe = llm_client.describe_image_model()
    if probe.get("ok"):
        return "gemini", "auto → gemini"
    return "local", f"auto → local ({probe.get('kind', 'unavailable')})"


def render_local(scene: dict, size: tuple[int, int], seed: int) -> Image.Image:
    """Build one styled set procedurally."""
    return build_background(scene, size, seed)


def _gemini_background(scene: dict, size: tuple[int, int]) -> Image.Image:
    raw = llm_client.generate_image(scene["prompt"], aspect_ratio="9:16")
    img = Image.open(io.BytesIO(raw)).convert("RGB")
    return im.fit_cover(img, size)


def generate_backgrounds(job_dir: str | Path, seed: int, canvas: dict,
                         provider: str, on_scene=None) -> list[dict]:
    job_dir = Path(job_dir)
    size = (int(canvas["width"]), int(canvas["height"]))
    scenes = get_scenes()
    results = []

    for idx, scene in enumerate(scenes):
        path = job_dir / f"bg_{scene['id']}.png"
        if provider == "gemini":
            img = _gemini_background(scene, size)
        else:
            img = render_local(scene, size, seed)
        img.save(path, "PNG")
        results.append({"scene_id": scene["id"], "path": str(path), "source": provider})
        if on_scene:
            on_scene(idx + 1, len(scenes), scene["id"])
    return results
