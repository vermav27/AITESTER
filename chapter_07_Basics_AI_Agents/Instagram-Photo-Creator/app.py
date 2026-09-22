"""Layer 0 - Web UI (Flask). The only user-facing surface.

Upload -> start job -> poll status -> preview -> download / recreate, plus Settings for the
LLM connection with a live Test connection action.

Never does pixel work (that lives in tools/). Never returns the API key (W1).
Architecture: architecture/07_web-ui.md
"""
from __future__ import annotations

import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

from flask import (Flask, abort, jsonify, render_template, request,
                   send_file, send_from_directory)
from werkzeug.utils import secure_filename

from config import (TMP_DIR, ensure_dirs, load_settings, save_settings,
                    settings_for_browser)
from tools import llm_client
from tools.ingest import validate as validate_upload
from tools.lib.errors import JobFailed
from tools.lib.scenes import get_scenes, scenes_public
from tools.run_job import run_job

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB (upload limit is 15 MB)

JOBS: dict[str, dict] = {}
JOBS_LOCK = threading.Lock()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _new_job(source_path: str, product_name: str, product_category: str, seed: int,
             parent: str | None = None) -> dict:
    job_id = uuid.uuid4().hex[:12]
    job = {
        "id": job_id,
        "state": "queued",
        "stage": "queued",
        "progress": 0,
        "message": "Queued",
        "outputs": [],
        "error": None,
        "seed": seed,
        "source_path": source_path,
        "product_name": product_name,
        "product_category": product_category,
        "parent": parent,
        "created_at": _now(),
        "manifest": None,
    }
    with JOBS_LOCK:
        JOBS[job_id] = job
    return job


def _update(job_id: str, **fields) -> None:
    with JOBS_LOCK:
        if job_id in JOBS:
            JOBS[job_id].update(fields)


def _worker(job: dict) -> None:
    job_id = job["id"]
    tmp_job_dir = Path(TMP_DIR) / job_id
    tmp_job_dir.mkdir(parents=True, exist_ok=True)

    # copy the already-validated upload into this job's tmp dir
    src = Path(job["source_path"])
    ext = src.suffix.lower()
    staged = tmp_job_dir / f"upload{ext}"
    try:
        staged.write_bytes(src.read_bytes())
    except OSError as exc:
        _update(job_id, state="failed", stage="error", error=f"Could not stage upload: {exc}")
        return
    try:
        src.unlink()
    except OSError:
        pass

    def on_progress(stage: str, pct: int, message: str = "") -> None:
        _update(job_id, state="running", stage=stage, progress=pct, message=message)

    try:
        result = run_job(
            job_id=job_id, source_path=str(staged),
            product_name=job["product_name"], product_category=job["product_category"],
            seed=job["seed"], on_progress=on_progress,
        )
        # move the staged original into the job dir so Recreate can reuse it
        with JOBS_LOCK:
            JOBS[job_id].update({
                "state": "done", "stage": "done", "progress": 100,
                "message": "Done", "outputs": result["outputs"],
                "manifest": result["manifest"],
                "source_path": str(staged),
                "out_dir": result["out_dir"], "zip": result["zip"],
                "zip_name": Path(result["zip"]).name,
                "backend_note": result["manifest_data"]["backend"]["note"],
            })
    except JobFailed as exc:
        _update(job_id, state="failed", stage=exc.stage, error=exc.message)
    except Exception as exc:  # noqa: BLE001 - surface any unexpected failure to the UI
        _update(job_id, state="failed", stage="error", error=f"{type(exc).__name__}: {exc}")


def _start(job: dict) -> None:
    t = threading.Thread(target=_worker, args=(job,), daemon=True)
    t.start()


@app.route("/")
def index():
    s = load_settings()
    return render_template("index.html", scenes=scenes_public(),
                           brand=s["brand"], canvas=s["canvas"],
                           background_provider=s["background_provider"])


@app.route("/generate", methods=["POST"])
def generate():
    if "image" not in request.files:
        return jsonify({"error": "No file uploaded."}), 400
    upload = request.files["image"]
    if not upload.filename:
        return jsonify({"error": "Empty filename."}), 400

    ext = Path(secure_filename(upload.filename)).suffix.lower()
    staging = Path(TMP_DIR) / "staging"
    staging.mkdir(parents=True, exist_ok=True)
    tmp_path = staging / f"{uuid.uuid4().hex[:8]}{ext}"
    upload.save(tmp_path)

    try:
        validate_upload(tmp_path)  # W4: validate BEFORE any API spend
    except JobFailed as exc:
        tmp_path.unlink(missing_ok=True)
        return jsonify({"error": exc.message, "kind": exc.kind}), 400

    seed = int(request.form.get("seed") or 42)
    job = _new_job(str(tmp_path),
                   request.form.get("product_name", "").strip()[:120],
                   request.form.get("product_category", "").strip()[:60], seed)
    _start(job)
    return jsonify({"job_id": job["id"]}), 202


@app.route("/recreate/<job_id>", methods=["POST"])
def recreate(job_id: str):
    with JOBS_LOCK:
        parent = JOBS.get(job_id)
    if not parent:
        return jsonify({"error": "Unknown job."}), 404
    if not parent.get("source_path") or not Path(parent["source_path"]).exists():
        return jsonify({"error": "Original upload is no longer available."}), 409

    seed = int(parent.get("seed", 42)) + 1
    job = _new_job(parent["source_path"], parent.get("product_name", ""),
                   parent.get("product_category", ""), seed, parent=job_id)
    _start(job)
    return jsonify({"job_id": job["id"], "seed": seed}), 202


@app.route("/status/<job_id>")
def status(job_id: str):
    with JOBS_LOCK:
        job = JOBS.get(job_id)
        if not job:
            return jsonify({"error": "Unknown job."}), 404
        return jsonify({
            "state": job["state"], "stage": job["stage"], "progress": job["progress"],
            "message": job["message"], "error": job["error"], "seed": job["seed"],
            "outputs": job["outputs"], "parent": job["parent"],
            "zip_name": job.get("zip_name"),
        })


@app.route("/result/<job_id>/<int:n>")
def result(job_id: str, n: int):
    with JOBS_LOCK:
        job = JOBS.get(job_id)
    if not job or job["state"] != "done":
        abort(404)
    match = next((o for o in job["outputs"] if o["index"] == n), None)
    if not match:
        abort(404)
    out_dir = Path(job["out_dir"])
    return send_from_directory(out_dir, Path(match["path"]).name, mimetype="image/jpeg")


@app.route("/download/<job_id>.zip")
def download(job_id: str):
    with JOBS_LOCK:
        job = JOBS.get(job_id)
    if not job or job["state"] != "done":
        abort(404)
    return send_file(job["zip"], as_attachment=True,
                     download_name=f"instagram-{job_id}.zip", mimetype="application/zip")


@app.route("/settings", methods=["GET"])
def settings_get():
    return render_template("settings.html", settings=settings_for_browser())


@app.route("/settings", methods=["POST"])
def settings_post():
    data = request.get_json(silent=True) or request.form.to_dict()
    patch: dict = {}
    if "background_provider" in data:
        patch["background_provider"] = str(data["background_provider"]).lower()
    llm = {}
    for key in ("provider", "base_url", "text_model", "image_model"):
        if data.get(key):
            llm[key] = str(data[key]).strip()
    if data.get("api_key"):
        llm["api_key"] = str(data["api_key"]).strip()
    if llm:
        patch["llm"] = llm
    brand = {}
    for key in ("handle", "position"):
        if data.get(key):
            brand[key] = str(data[key]).strip()
    for key in ("opacity", "size_pct"):
        if data.get(key) not in (None, ""):
            try:
                brand[key] = float(data[key])
            except (TypeError, ValueError):
                pass
    if brand:
        patch["brand"] = brand
    save_settings(patch)
    return jsonify({"ok": True, "settings": settings_for_browser()})


@app.route("/settings/test", methods=["POST"])
def settings_test():
    data = request.get_json(silent=True) or {}
    # Test an unsaved key if one was typed, WITHOUT persisting it (never clobber a working key).
    override = {k: data[k] for k in
                ("provider", "base_url", "text_model", "image_model", "api_key") if data.get(k)}
    result = llm_client.test_connection(override or None)
    return jsonify(result), (200 if result["ok"] else 502)


@app.route("/healthz")
def healthz():
    return jsonify({"ok": True, "jobs": len(JOBS)})


@app.errorhandler(413)
def too_large(_):
    return jsonify({"error": "File exceeds the 15 MB limit."}), 413


ensure_dirs()

if __name__ == "__main__":
    s = load_settings()
    print("\n  Instagram-Photo-Creator  ·  B.L.A.S.T. / A.N.T.")
    print(f"  brand      : {s['brand']['handle']}")
    print(f"  canvas     : {s['canvas']['width']}x{s['canvas']['height']} 9:16")
    print(f"  backgrounds: {s['background_provider']}")
    print("  →  http://127.0.0.1:5001\n")
    app.run(host="127.0.0.1", port=5001, debug=False, threaded=True)
