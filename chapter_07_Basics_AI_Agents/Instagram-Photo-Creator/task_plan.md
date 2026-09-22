# task_plan.md — Phases, Goals & Checklists

> **Project:** Instagram-Photo-Creator
> **Protocol:** B.L.A.S.T. (Blueprint · Link · Architect · Stylize · Trigger) with A.N.T. 3-layer architecture
> **Current stage:** ✅ Phases 1–4 complete — built, run and live-tested (2026-09-22)
> **Status:** 🟢 RUNNING LOCALLY at `http://127.0.0.1:5001` (`python app.py`)
> **Confirmed scope:** LLM link = **Gemini** · Backgrounds = **local procedural renderer** (Gemini behind the adapter, see `LLM.md` ADR-8) · Interface = **Flask web UI** · Reel = **4 independent scenes** · Watermark = **@meraki.by.ankita**

---

## 1. North Star (Goal)

> **Input:** ONE raw product photo (JPG/PNG, any framing).
> **Output:** FOUR professionally edited Instagram photos, **9:16**, **4K (2160×3840)**, so they can be stitched into a Reel.
> **Hard constraint:** Product **color, identity, logo, shape must NOT change**. Only environment/lighting/crop may change.

**Success criteria (all must pass):**

| # | Criterion | How it's verified |
|---|-----------|-------------------|
| 1 | Exactly 4 output images | File count assert |
| 2 | Each is exactly 2160×3840 (9:16) | PIL `size` assert |
| 3 | Product region color unchanged | ΔE2000 ≤ 3.0 on the opaque product core vs. source |
| 4 | Product pixel structure preserved | SSIM ≥ 0.95 on the opaque product core |
| 5 | Visually professional (no halo/artifacts) | Human review + edge-quality check |
| 6 | Deterministic re-run | Same seed + inputs → byte-identical (modulo encoder) |

---

## 2. Phase Checklist

### 🟢 Protocol 0 — Initialization
- [x] Create `task_plan.md`
- [x] Create `findings.md`
- [x] Create `progress.md`
- [x] Create `LLM.md` (Project Constitution)
- [x] **Discovery Questions answered** (see §3)
- [x] **Data Schema signed off** in `LLM.md` (§3.1–3.5)
- [x] **Blueprint approved** (this file)
- [x] ⛔ Halt lifted → `tools/` written

### 🏗️ Phase 1 — B: Blueprint (Vision & Logic)
- [x] Answer the 5 Discovery Questions
- [x] Lock Input/Output JSON Schema in `LLM.md` (§3) — incl. settings schema §3.5
- [x] Research: scan for identity-preserving image-edit pipelines (findings F1–F7)
- [x] Decide backends → LLM link **Gemini**; backgrounds **local renderer** (live 429 forced ADR-8)
- [x] Write the 4 scene recipes (marble / velvet / travertine / botanical) → `tools/lib/scenes.py`
- [x] Get blueprint sign-off

### ⚡ Phase 2 — L: Link (Connectivity)
- [x] Create `.env` with `GEMINI_API_KEY` (+ model + provider vars) + `.env.example`
- [x] `tools/check_env.py` → validates config and runs the live handshake
- [x] `tools/llm_client.py` → text probe + image probe + image generation, one adapter
- [x] Confirm handshake: text **OK**, image **429 → provider falls back to local**
- [x] Upload validation gate (ext / ≤15 MB / ≥1000 px long edge) before any API spend

### ⚙️ Phase 3 — A: Architect (3-Layer Build)
- [x] `architecture/` SOPs written (00 overview, 01 input, 02 segment, 03 backgrounds, 04 composite, 05 canvas+watermark, 06 verify+export, 07 web-ui)
- [x] Layer 3 tools implemented (atomic, testable):
  - [x] `tools/ingest.py` — validate, EXIF-safe load, sRGB normalize, sha256
  - [x] `tools/segment.py` — rembg `isnet-general-use` + Lab-threshold fallback + edge de-contamination
  - [x] `tools/generate_backgrounds.py` — 4 empty 9:16 styled sets; local renderer or Gemini
  - [x] `tools/lib/textures.py` — procedural materials, architecture, light and atmosphere
  - [x] `tools/composite.py` — paste **original** product pixels + cast/contact shadow, reflection, halo
  - [x] `tools/enforce_canvas.py` — exact 2160×3840, cover-scale → center-crop
  - [x] `tools/watermark.py` — one small `@meraki.by.ankita` mark
  - [x] `tools/verify.py` — canvas / coverage / ΔE / SSIM gate on the opaque core, fails the job on breach
  - [x] `tools/export.py` — `output/<job_id>/NN_scene.jpg` + `manifest.json` + ZIP
  - [x] `tools/run_job.py` — Layer-2 router (ingest → … → export) with progress callbacks
- [x] Layer 2 Navigation routing logic
- [x] Web layer: `app.py` (Flask) — calls `run_job.py`, never touches pixel math
- [x] `.tmp/` for intermediates; `output/` is the only deliverable dir
- [x] Golden Rule honored: SOPs written *before* the code

### ✨ Phase 4 — S: Stylize (Web UI)
- [x] Upload screen: drag-drop / file picker, product name + category inputs, file preview
- [x] Progress screen: per-stage status + bar (ingest → segment → 4× generate → composite → verify → export)
- [x] Results screen: 4 thumbnails at 9:16, per-image ΔE/SSIM badge, per-image download, "Download all (ZIP)"
- [x] **Recreate** button → new job, same source, seed+1
- [x] Clear error surface when the fidelity gate fails (shows the stage + reason)
- [x] Settings screen: LLM connection (provider / key / base URL / text model / image model) + **Test connection** + background provider + watermark controls
- [x] Clean CSS, mobile-friendly, key never returned to the browser
- [x] Sets are materials + architecture + lighting (no flat gradients); each set's shadow follows its key light

### 🚀 Phase 5 — T: Trigger
- [x] Launch: `python app.py` → open `http://127.0.0.1:5001`
- [ ] (Optional) watch-folder / batch mode
- [ ] (Optional) 1080×1920 companion exports for direct IG upload (4K masters kept)

---

## 3. Discovery Questions (BLAST Phase 1) — ✅ ANSWERED

| # | Question | Answer |
|---|----------|--------|
| Q1 | **North Star** — one reel or standalone posts? | **4 independent scenes** (marble, velvet, travertine, botanical) that also stitch cleanly into one reel |
| Q2 | **Integrations** — which backend? | **Gemini 2.5 Flash Image** (`gemini-2.5-flash-image-preview`), Google AI Studio key |
| Q3 | **Source of Truth** — where do raw photos live? | **User upload via web UI** (bytes in memory → `.tmp/<job_id>/`) |
| Q4 | **Delivery Payload** — where do outputs go? | **Web UI preview + download** (per-file and ZIP); also written to `output/<job_id>/` |
| Q5 | **Behavioral Rules** — "Do Not" list | Defaults adopted (see `LLM.md` §4): no grading, no logo morph, no occluding props, no text overlays. *User may extend.* |

**Still open:** product category for the first test (bottle? garment? electronics?) — affects segmentation difficulty and scene recipes. Can be supplied with the first uploaded photo.

> ✅ **Resolved 2026-09-22.** First real subject = the supplied sample `Input/Test.JPG`: a handmade
> **macramé rainbow wall hanging** on a plain wall, category `home_decor`; it is now the baseline used
> in every test in `TESTPLAN.md`.

---

## 4. Definition of Done

- [x] All success criteria (§1) pass on a real raw photo — `Input/Test.JPG`, 4/4 images
- [x] Web UI: upload → 4 previews → ZIP download works end-to-end (verified over HTTP + in-browser)
- [x] `output/<job_id>/manifest.json` records seed, backend, ΔE, SSIM per image
- [x] `findings.md` and `progress.md` kept current through every phase
- [x] Zero manual pixel edits required by the user
- [x] Recreate produces a fresh set without re-uploading
- [x] Settings → LLM connection with a live Test connection
- [x] Key is masked in every browser-facing response
