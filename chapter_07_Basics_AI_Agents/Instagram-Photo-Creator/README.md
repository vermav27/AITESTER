# Instagram Photo Creator

One uploaded product photo → **four** professionally composed, aesthetic Instagram photos at
**2160×3840 (9:16, 4K)**, each carrying one small `@meraki.by.ankita` watermark — ready to stitch
into a Reel. The product's **colour, logo, shape and identity are never regenerated** by a model:
the product is cut out with a real alpha matte and its **original pixels are pasted back** onto a
generated backdrop, then a numeric gate (ΔE2000 ≤ 3.0, SSIM ≥ 0.95) decides whether an image ships.

Built with the **B.L.A.S.T.** protocol on an **A.N.T. 3-layer architecture**.

---

## Run it

```bash
cd chapter_07_Basics_AI_Agents/Instagram-Photo-Creator
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python app.py
# open http://127.0.0.1:5001
```

> Port **5001**, not 5000 — macOS AirPlay Receiver owns 5000. Change it at the bottom of `app.py`.

First run downloads a one-off 179 MB `isnet-general-use` ONNX model into `.tmp/models/`.
If that download isn't possible, `segment.py` falls back to a Lab colour-distance mask with no network.

## Use it

1. **Upload** — drop a JPG/PNG/WEBP (long edge ≥ 1000 px, ≤ 15 MB). Optionally name the product.
2. **Create 4 photos** — the job runs on a background thread; the page polls and shows each stage.
3. **Your photos** — four 9:16 previews with ΔE/SSIM badges. Download any one, or **Download all (ZIP)**.
4. **Recreate** — click to roll a fresh set from the same upload (new seed, no re-upload).
5. **Settings** — configure the LLM connection and hit **Test connection** for a live check.

## The four sets

Each is a styled **room** — a wall material, a floor material, a cove between them, architecture,
a directional key light and atmosphere — not a gradient.

| id | Set | Backdrop |
|----|-----|----------|
| `marble` | **Polished Calacatta** | book-matched marble wall + glossy marble floor, raking daylight from the upper left, floor reflection |
| `velvet` | **Emerald Velvet** | deep emerald drapes in vertical folds + velvet floor, one warm raking light from the right |
| `travertine` | **Travertine Atelier** | bedded travertine wall with an **arched niche**, stone floor, diagonal window light + blind shadow |
| `botanical` | **Botanical Salon** | mottled sage plaster with leaf dapple + greenery bokeh, oak plank floor, airy top light |

Every set throws the product's shadow **away from its own key light**, and adds a contact shadow plus
a floor reflection on glossy surfaces.

## Architecture

```
app.py            Layer 0  Flask UI: upload → job → poll → preview → download / recreate. No pixel work.
architecture/     Layer 1  SOPs (00 overview … 07 web-ui). Golden Rule: SOP changes before code.
tools/run_job.py  Layer 2  Routing: ingest → segment → generate → composite → canvas → watermark → verify → export
tools/*.py        Layer 3  Atomic, deterministic tools. tools/lib/ holds shared helpers.
```

| Tool | Responsibility |
|------|----------------|
| `tools/ingest.py` | validate (ext/size/resolution), EXIF-safe load, sRGB normalize, sha256 |
| `tools/segment.py` | real alpha matte — rembg `isnet-general-use`, Lab-threshold fallback, edge de-contamination |
| `tools/lib/textures.py` | procedural materials & light: marble, travertine, velvet, oak, plaster, arch niche, dapple, bokeh, glow |
| `tools/lib/scenes.py` | the four sets — palette, prompt and pixel build |
| `tools/generate_backgrounds.py` | four **empty** 9:16 sets (local renderer, or Gemini when quota allows) |
| `tools/composite.py` | paste the **original** product pixels, grounded by cast/contact shadow, floor reflection, halo |
| `tools/enforce_canvas.py` | exact 2160×3840 — cover-scale → center-crop, never stretch |
| `tools/watermark.py` | one small `@meraki.by.ankita` mark (text width ≈ 15 % of the canvas) |
| `tools/verify.py` | the gate: canvas, coverage, ΔE2000, SSIM on the product's opaque core, watermark presence |
| `tools/export.py` | `output/<job_id>/NN_scene.jpg` + `manifest.json` + ZIP |
| `tools/llm_client.py` | the only HTTP client — Gemini adapter, `test_connection`, image generation |

## Configuration

`.env` (gitignored; see `.env.example`) supplies defaults; the **Settings** screen writes
`settings.json` on top of them.

```
GEMINI_API_KEY=…            # never sent to the browser; masked in every response
GEMINI_TEXT_MODEL=gemini-3.6-flash     # used by "Test connection"
GEMINI_IMAGE_MODEL=gemini-3.1-flash-image
BACKGROUND_PROVIDER=auto    # auto | local | gemini
BRAND_HANDLE=@meraki.by.ankita
```

## Important note on the supplied key

`GET /v1beta/models` + live probes show the provided key authenticates with the **`x-goog-api-key`**
header and works for **text**, but **every Gemini image model returns HTTP 429 with free-tier
quota limit 0** (`gemini-2.5-flash-image`, `gemini-3.1-flash-image`, `gemini-3.1-flash-lite-image`,
`gemini-3-pro-image`). Backgrounds therefore come from the **local procedural renderer** by default —
the product-pixel guarantee is unchanged. Point `background_provider` at `gemini` once a key with
image quota is available and the model takes over with no code change. See `findings.md` F10.

## Verification & docs

| File | What's in it |
|------|--------------|
| `LLM.md` | the constitution — schemas, invariants, behavioural rules, decisions |
| `architecture/` | the Layer-1 SOPs |
| `findings.md` | research, the live API probe, measured results |
| `progress.md` | work log with errors and results |
| `task_plan.md` | phases, goals, checklists |
| `TESTPLAN.md` | 44 checks with observed results |
| `tools/selftest.py` | `python tools/selftest.py --network` → 20/20 |
| `tools/check_env.py` | the Phase-2 handshake gate |

## Output layout

```
.tmp/<job_id>/     source_srgb.png · product_rgba.png · mask.png · bg_<scene>.png · final_<scene>.png
output/<job_id>/   01_marble.jpg · 02_velvet.jpg · 03_travertine.jpg · 04_botanical.jpg
                   manifest.json  (seed, backend, per-image ΔE/SSIM)  · <job_id>.zip
```

Measured on the sample upload: ΔE2000 **0.05–0.19** (gate ≤ 3.0) and SSIM **0.999** (gate ≥ 0.95) —
i.e. the product's own pixels came through untouched.
