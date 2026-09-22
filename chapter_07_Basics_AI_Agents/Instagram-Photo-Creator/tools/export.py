"""Export (Layer 3): write deliverables + manifest + ZIP. The only writer to output/.

Contract: architecture/06_verify-export.md
"""
from __future__ import annotations

import json
import zipfile
from pathlib import Path

from PIL import Image

from config import OUTPUT_DIR

JPEG_KW = {"quality": 95, "subsampling": 0, "optimize": True}


def export(job_id: str, finals: list[dict], manifest_base: dict,
           out_root: str | Path | None = None) -> dict:
    """finals: [{index, scene_id, image(PIL), metrics, verdict}]"""
    out_dir = Path(out_root or OUTPUT_DIR) / job_id
    out_dir.mkdir(parents=True, exist_ok=True)

    outputs = []
    for item in finals:
        name = f"{item['index']:02d}_{item['scene_id']}.jpg"
        path = out_dir / name
        item["image"].save(path, "JPEG", **JPEG_KW)
        outputs.append({
            "index": item["index"],
            "scene_id": item["scene_id"],
            "path": str(path.relative_to(Path(out_root or OUTPUT_DIR))),
            "width": item["image"].width,
            "height": item["image"].height,
            "metrics": item["metrics"],
            "verdict": item["verdict"],
        })

    manifest = dict(manifest_base)
    manifest["outputs"] = outputs
    manifest["status"] = "success"
    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))

    zip_path = out_dir / f"{job_id}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for item in outputs:
            zf.write(out_dir / Path(item["path"]).name, Path(item["path"]).name)
        zf.write(manifest_path, manifest_path.name)

    return {
        "out_dir": str(out_dir),
        "manifest": str(manifest_path),
        "zip": str(zip_path),
        "outputs": outputs,
    }
