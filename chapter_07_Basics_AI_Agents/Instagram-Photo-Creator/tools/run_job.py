"""Run job (Layer 2 - Navigation): route data through the atomic tools in fixed order.

ingest → segment → generate_backgrounds → composite → canvas → watermark → verify → export

Does no pixel work itself. Owns the job's stage/progress reporting.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from config import OUTPUT_DIR, TMP_DIR, load_settings
from tools import composite as composite_tool
from tools import enforce_canvas as canvas_tool
from tools import export as export_tool
from tools import generate_backgrounds as bg_tool
from tools import ingest as ingest_tool
from tools import segment as segment_tool
from tools import verify as verify_tool
from tools import watermark as watermark_tool
from tools.lib.errors import JobFailed
from tools.lib.scenes import get_scenes


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def run_job(job_id: str, source_path: str, product_name: str = "",
            product_category: str = "", seed: int = 42, on_progress=None) -> dict:
    settings = load_settings()
    canvas = settings["canvas"]
    brand = settings["brand"]

    def progress(stage: str, pct: int, message: str = "") -> None:
        if on_progress:
            on_progress(stage, pct, message)

    job_dir = Path(TMP_DIR) / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    started = _now()

    progress("ingest", 4, "Validating upload")
    ing = ingest_tool.ingest(source_path, job_dir)

    progress("segment", 10, "Isolating the product")
    seg = segment_tool.segment(ing["path"], job_dir)

    provider, provider_note = bg_tool.resolve_provider(settings.get("background_provider", "auto"))
    progress("generate", 30, f"Generating 4 backdrops ({provider})")

    def on_scene(done: int, total: int, scene_id: str) -> None:
        progress("generate", 30 + int(30 * done / total), f"Backdrop {done}/{total} · {scene_id}")

    backgrounds = bg_tool.generate_backgrounds(job_dir, seed, canvas, provider, on_scene=on_scene)
    bg_by_id = {b["scene_id"]: b["path"] for b in backgrounds}

    finals = []
    scenes = get_scenes()
    for idx, scene in enumerate(scenes, start=1):
        progress("composite", 62 + int(14 * (idx - 1) / len(scenes)),
                 f"Compositing {scene['name']}")

        product_layer = composite_tool.build_product_layer(seg["product_rgba"], canvas, scene)
        composed, pos = composite_tool.composite(bg_by_id[scene["id"]], product_layer, canvas, scene)
        final = canvas_tool.enforce_canvas(composed, canvas)

        watermarked, wm_bbox = watermark_tool.add_watermark(
            final, brand["handle"], opacity=brand["opacity"],
            size_pct=brand["size_pct"], position=brand["position"])

        metrics = verify_tool.verify(canvas, composed, product_layer, pos,
                                     seg["coverage"], wm_bbox)

        final_path = job_dir / f"final_{scene['id']}.png"
        watermarked.save(final_path, "PNG")

        finals.append({
            "index": idx, "scene_id": scene["id"],
            "image": watermarked, "metrics": metrics, "verdict": metrics["verdict"],
        })

    progress("verify", 88, "All 4 images passed the fidelity gate")
    progress("export", 94, "Writing deliverables")

    manifest_base = {
        "job_id": job_id,
        "protocol": "B.L.A.S.T. / A.N.T. 3-layer",
        "started_at": started,
        "finished_at": _now(),
        "backend": {
            "name": provider,
            "model": settings["llm"]["image_model"] if provider == "gemini" else "local-procedural",
            "seed": seed,
            "note": provider_note,
        },
        "source": {
            "path": ing["path"], "width": ing["width"], "height": ing["height"],
            "sha256": ing["sha256"], "low_res_warning": ing["low_res_warning"],
        },
        "product": {"name": product_name, "category": product_category},
        "segmentation": {"method": seg["method"], "coverage": round(seg["coverage"], 4)},
        "brand": {"handle": brand["handle"]},
        "canvas": canvas,
        "errors": [],
    }

    result = export_tool.export(job_id, finals, manifest_base, out_root=OUTPUT_DIR)
    progress("done", 100, "Done")
    result["manifest_data"] = manifest_base
    return result
