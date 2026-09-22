# findings.md — Research, Discoveries & Constraints

> **Project:** Instagram-Photo-Creator · **Stage:** Protocol 0 (research in progress)
> Each finding records: what we learned, why it matters, and the concrete request (curl/command) we'd use.

---

## F1 — The core problem: "edit the photo" vs. "regenerate the photo"

**Finding.** Text-to-image models (pure txt2img) **cannot** guarantee an unchanged product. They hallucinate new pixels, shift hues, and re-draw logos. Any prompt-only approach *will* violate the "don't change color/identity" constraint — it just hides it behind "looks similar".
**Matters.** This kills the naive plan of `prompt = "put this bottle on marble"`. It forces an **identity-preserving** design.
**Consequence.** We adopt a **masked-composite pipeline** (see F2, and `LLM.md` invariant #1).

---

## F2 — The winning architecture: mask → generate *background only* → composite original pixels

**Finding.** If we (a) cut out the product with an alpha mask and (b) only ever **paste the ORIGINAL product pixels** back over a generated background, then color/identity preservation becomes a **mathematical guarantee**, not a hope. No model ever touches the product's pixels.
**Matters.** This is the difference between "AI guessed and got close" and "deterministic and provable".
**Pipeline.**
```
raw.jpg
  └─ segment  →  product_rgba.png  (alpha mask, original pixels intact)
  └─ generate →  background_9x16.png × 4 scenes   (model edits BLANK/background only)
  └─ composite→  paste product_rgba onto background (pixel-exact product)
  └─ canvas   →  crop/pad to 2160×3840, upscale (Real-ESRGAN x4 + Lanczos)
  └─ verify   →  ΔE2000 ≤ 3.0 & SSIM ≥ 0.95 on masked region, or FAIL
```
**Edge case.** Segmentation halos (the old background bleeding into semi-transparent edges). Fix: alpha matting / edge de-contamination (trimap + `pymatting`) **before** compositing, else the product edge carries a color fringe.

---

## F3 — Candidate image-edit backends (for the *background* generation)

| Backend | Identity safe? | 9:16 native? | 4K native? | Cost | Notes |
|---------|----------------|--------------|------------|------|-------|
| **Gemini 2.5 Flash Image** ("nano-banana") | Strong (instruction-edit) | ✅ `aspectRatio: 9:16` | ❌ ~1MP | paid/free tier | Best all-rounder for scene synthesis + relight |
| **FLUX.1 Kontext [pro]** (BFL) | Strong (context edit) | ✅ `aspect_ratio` | ❌ ≤2MP | paid | Excellent "reframe while keeping subject" |
| **OpenAI `gpt-image-1` edits** | Good | ⚠️ `1024x1536` max | ❌ | paid | Size capped, needs upscale |
| **Local ComfyUI (Flux Kontext GGUF + IP-Adapter)** | Strong | ✅ (set latent) | ❌ | free/GPU | Fully offline, no per-image cost, slower setup |

**Conclusion.** All are **sub-4K** → the upscale step (`enforce_canvas.py`) is **mandatory regardless of backend**. ✅ **CHOSEN: Gemini 2.5 Flash Image** (fastest to a working demo, native 9:16). The backend sits behind a thin adapter so FLUX / ComfyUI can be swapped in later without touching the tools.

### Curl — Gemini 2.5 Flash Image (9:16, background synthesis)
```bash
B64=$(base64 -i raw_background_or_prompt.png | tr -d '\n')
curl -s -X POST \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image-preview:generateContent" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{
      "parts": [
        {"text": "Generate a clean 9:16 vertical studio background: matte beige seamless, soft top-left key light, gentle floor shadow area in the lower third. Empty scene, no product, no text. Professional e-commerce photography."}
      ]
    }],
    "generationConfig": {
      "responseModalities": ["IMAGE"],
      "imageConfig": { "aspectRatio": "9:16" }
    }
  }' \
  | jq -r '.candidates[0].content.parts[] | select(.inlineData) | .inlineData.data' \
  | base64 --decode > backgrounds/studio.png
```

### Curl — FLUX.1 Kontext (alternative backend, subject-preserving reframe)
```bash
curl -s -X POST "https://api.bfl.ai/v1/flux-kontext-pro" \
  -H "x-key: $BFL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Extend the scene vertically to 9:16 with a seamless studio floor and soft gradient wall. Keep the product completely unchanged in color, shape, and logo.",
    "input_image": "'"$B64"'",
    "aspect_ratio": "9:16",
    "output_format": "jpeg",
    "safety_tolerance": 2
  }'
# → { "id": "abc", "polling_url": "https://api.bfl.ai/v1/get_result?id=abc" }

curl -s "https://api.bfl.ai/v1/get_result?id=abc" -H "x-key: $BFL_API_KEY" | jq '{status, sample}'
```

### Curl — OpenAI gpt-image-1 edits (source image in, edited image out)
```bash
curl -s -X POST "https://api.openai.com/v1/images/edits" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -F "model=gpt-image-1" \
  -F "image[]=@raw.jpg" \
  -F "prompt=Replace only the background with a warm minimalist wooden desk; keep the product exactly as-is. Vertical 9:16 composition." \
  -F "size=1024x1536" \
  -o out.json
jq -r '.data[0].b64_json' out.json | base64 --decode > edited.png
```

---

## F4 — Segmentation options (the mask step)

| Tool | Type | Notes |
|------|------|-------|
| **rembg** (`u2net`, `isnet-general-use`) | Python pkg | Fastest to integrate, one line, CPU ok |
| **SAM 2 / SAM** (Meta) | Promptable | Best quality, needs click/box prompt or auto-mask |
| **BiRefNet** | SOTA matting | Best edges for product cutouts, heavier |

**Curl/pip:**
```bash
pip install "rembg[cpu]" onnxruntime pillow numpy scikit-image pymatting
```
```bash
# quick CLI mask (produces transparent PNG, original RGB preserved)
rembg i raw.jpg product_rgba.png
```

---

## F5 — Upscaling to true 4K (2160×3840)

**Finding.** No edit API returns 4K. We upscale **after** compositing so the product is upscaled **once**, together with its background (avoids a sharp-product-on-soft-bg mismatch).
**Matters.** Upscaling product and background separately causes a visible "cutout" seam.

```bash
# Real-ESRGAN (GPU/Vulkan) — x4, then Lanczos to exact canvas
realesrgan-ncnn-vulkan -i composed.png -o composed_4x.png -n realesrgan-x4plus -s 4
```
```python
# deterministic final canvas: exact 2160×3840, centered, no distortion
from PIL import Image
img = Image.open("composed_4x.png")
scale = max(2160 / img.width, 3840 / img.height)          # cover
img = img.resize((round(img.width*scale), round(img.height*scale)), Image.LANCZOS)
left, top = (img.width-2160)//2, (img.height-3840)//2     # center-crop
img.crop((left, top, left+2160, top+3840)).save("final.jpg", quality=95, subsampling=0)
```

---

## F6 — How to *prove* the product didn't change (verification math)

**Finding.** "It looks the same" is not a gate. We need a numeric pass/fail.
- **ΔE2000** (CIEDE2000 color difference) on the masked product region, source vs. output: **≤ 3.0** (≤1.0 = imperceptible, ≤2.0 = barely perceptible). Because we paste original pixels, expected ΔE ≈ 0 pre-upscale; the gate catches accidental grading.
- **SSIM** on the masked region: **≥ 0.95** (structure/shape/logos intact).
- Note: if the upscaler smooths detail, compute ΔE/SSIM on the **pre-upscale composite** and re-run a looser post-upscale sanity check.

```python
import numpy as np
from skimage.metrics import structural_similarity as ssim
from skimage.color import rgb2lab, deltaE_ciede2000

def product_fidelity(src_rgb, out_rgb, mask):
    m = mask > 128
    de = deltaE_ciede2000(rgb2lab(src_rgb/255.), rgb2lab(out_rgb/255.))[m].mean()
    s  = ssim(src_rgb, out_rgb, channel_axis=2, data_range=255,
              full=True)[0][m].mean()
    return {"deltaE": float(de), "ssim": float(s)}
# gate: de <= 3.0 and s >= 0.95, else raise JobFailed
```

---

## F7 — BLAST structural constraints (from `BLAST.md`)

- Protocol 0 forbids writing `tools/` scripts until Discovery is answered + schema locked + blueprint approved. **We are here.**
- 3-layer separation is mandatory: `architecture/` (SOP markdown) → Navigation (routing) → `tools/` (atomic deterministic Python).
- **Golden Rule:** change the SOP *before* the code.
- All secrets in `.env`; all intermediates in `.tmp/`.
- Python is the tooling language (per BLAST Phase 3, Layer 3).

**Implication for us.** Even though the *model* is probabilistic, everything we write in `tools/` (mask, composite, canvas, verify, export) is **deterministic**. The only probabilistic call is background generation, and it's sandboxed to the background region.

---

## F8 — Discovery: RESOLVED (2026-09-22)

| Question | Decision |
|----------|----------|
| Backend (Q2) | ✅ **Gemini 2.5 Flash Image** (`gemini-2.5-flash-image-preview`) |
| Input/Output (Q3/Q4) | ✅ **Web UI** — upload in, preview + download (ZIP) out |
| Reel style (Q1) | ✅ **4 independent scenes** that also stitch into one reel |
| Do-Not list (Q5) | ✅ Defaults adopted (`LLM.md` §4); user may extend |

**Consequence.** Phase 2 target = `GEMINI_API_KEY` handshake. Phase 4 = a real web UI, not a folder drop. See F9.

---

## F9 — Web UI stack (chosen after the answer to Q3/Q4)

**Finding.** A local Python pipeline needs a thin browser front-end. Two realistic options:

| Option | Pros | Cons |
|--------|------|------|
| **Flask + Jinja + vanilla JS** ✅ chosen | Same language as Layer 3 tools; trivial to call `run_job.py`; full control of the 9:16 preview grid; easy ZIP download | Must hand-write a bit of HTML/CSS |
| Streamlit | Fastest prototype, built-in file uploader | Awkward for a custom 4-up 9:16 gallery + per-image badges; heavy rerun model |

**Why Flask.** The tools are already Python functions; `app.py` just imports and calls them. Streamlit's rerun-on-interaction model fights a multi-minute, multi-stage job that must show progress.

**Consequences / constraints.**
- Gemini image calls take seconds-to-tens-of-seconds each; 4 of them → the job is **long-running**. So: run the job in a **background thread**, expose a `/status/<job_id>` endpoint, and have the browser poll. Don't block the request.
- Uploads must be validated *before* any API spend: mime type, min resolution (≥ 1000px on the long edge, else the 4K upscale is fake detail), max file size (~15 MB).
- Never expose `.env` or the API key to the browser. All Gemini calls happen server-side.
- Reel-readiness: the 4 outputs are independent shots, so the UI should also offer "Download all (ZIP)" and note that a 1080×1920 export is what IG actually ingests.

---

## F10 — Live probe of the supplied key (2026-09-22) — the finding that changed v1

**Finding.** The provided `GEMINI_API_KEY` authenticates with the header **`x-goog-api-key`**
(not `Authorization: Bearer` — that returns `401 API_KEY_SERVICE_BLOCKED`). It works for
**text**, but **every image model is quota-blocked**:

```bash
# text: works
curl -s -X POST \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent" \
  -H "x-goog-api-key: $GEMINI_API_KEY" -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"Reply with exactly: CONNECTION_OK"}]}]}'
# → {"candidates":[{"content":{"parts":[{"text":"CONNECTION_OK" ...

# image: 429, free-tier limit 0
curl -s -o /dev/null -w "%{http_code}\n" -X POST \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-image:generateContent" \
  -H "x-goog-api-key: $GEMINI_API_KEY" -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"red apple"}]}],"generationConfig":{"responseModalities":["IMAGE"]}}'
# → 429 RESOURCE_EXHAUSTED · generate_content_free_tier_requests · limit: 0
```

**Image models probed and their status** (from `GET /v1beta/models`):

| Model | Display name | Result |
|-------|--------------|--------|
| `gemini-2.5-flash-image` | Nano Banana | 429 (limit 0) |
| `gemini-3.1-flash-image` | Nano Banana 2 | 429 (limit 0) |
| `gemini-3.1-flash-lite-image` | Nano Banana 2 Lite | 429 (limit 0) |
| `gemini-3-pro-image` | Nano Banana Pro | 429 (limit 0) |

**Matters.** The original blueprint assumed `gemini-2.5-flash-image` would synthesize backgrounds.
It cannot, on this key. Shipping a Gemini-only pipeline would have produced a demo that 429s on
every image.

**Consequence → ADR-8.** Backgrounds are generated by a **deterministic local renderer**
(PIL gradients + radial light + vignette + seeded grain). Gemini stays behind the adapter; the
Settings screen exposes `background_provider = auto | local | gemini`, and `auto` probes once then
falls back. A key with image quota upgrades output with **no code change**.

**Also learned:** `models/gemini-2.5-flash` now returns `404 "no longer available to new users"`,
so `gemini-3.6-flash` is used as the text model for the connection test.

---

## F11 — Segmentation validated: `rembg` isnet-general-use works well on the sample

**Finding.** `rembg` (`isnet-general-use`) cleanly cuts the macramé wall hanging from its flat wall,
with **21.97 % coverage**, in ~19 s on CPU (first call includes a one-time 179 MB model download).
No halo was visible at 2160×3840 after a 1 px Gaussian feather.

```bash
U2NET_HOME="$PWD/.tmp/models" .venv/bin/python -c "
from rembg import remove, new_session
from PIL import Image
im = Image.open('Input/Test.JPG').convert('RGB')
remove(im, session=new_session('isnet-general-use')).save('.tmp/seg.png')"
```

**Matters.** This is the step that makes invariant I1 real: the product's RGB pixels survive
untouched and are re-pasted, so identity/colour preservation is a *construction guarantee*, not a hope.

**Edge case kept in code.** If `rembg` (or its ONNX weights) is unavailable, `segment.py` falls back
to a Lab colour-distance threshold + largest-connected-component mask — no network required.

---

## F12 — Verification numbers on the real sample (end-to-end)

**Finding.** Pasted-original compositing yields ΔE ≈ 0 on the solid product core. Measured on the
**opaque core at the exact placement rect**:

| # | scene | size | ΔE2000 | SSIM | verdict |
|---|-------|------|--------|------|---------|
| 1 | marble | 2160×3840 | 0.057 | 0.9989 | pass |
| 2 | velvet | 2160×3840 | 0.190 | 0.9997 | pass |
| 3 | travertine | 2160×3840 | 0.051 | 0.9991 | pass |
| 4 | botanical | 2160×3840 | 0.059 | 0.9990 | pass |

Both gates clear with huge margin (ΔE ≤ 3.0, SSIM ≥ 0.95). Whole job ≈ 27 s; ZIP ≈ 7.8 MB.

**Caveat / correction.** The first published numbers (ΔE 0.74–0.85, SSIM 0.980–0.986) were
**measurement artefacts**, not real drift:
1. the mask threshold (`> 128`) included the feathered edge, where the output is *designed* to blend
   with the backdrop — so the gate was partly grading the set;
2. the product rectangle was rebuilt from a rounded centre (`round(cx - w/2)`), which with
   round-half-to-even landed **one pixel off** the compositor's `left`, comparing shifted pixels.

Fix: `verify` now takes the compositor's `pos` dict, measures ΔE on `alpha ≥ 250`, and measures SSIM
on that mask **eroded by 3 px** so each SSIM window lies wholly inside the product. Recorded as
ADR-13 and in `architecture/06`.

---

## F13 — Why the first luxury pass looked flat (three bugs, all found by rendering and looking)

**Finding 1 — blown-out light layers.** `textures.tint(field, c_dark, c_light)` expects a **0–1**
field, but `glow()` and `linear_light()` passed 0–255 values. The light layer saturated to white and
`screen()` washed every set to ~[230,229,229] with a standard deviation of ~19 — velvet (intended deep
emerald) measured `[213,208,198]`. Fix: normalise (`strength / 255.0`). Velvet immediately measured
`[50,73,62]`.

**Finding 2 — `arch_niche` blacked out everything outside the arch.** It returned `m * shade`, which
is 0 wherever the mask is 0, so `multiply()` painted the whole frame black except the niche. Fix:
`1.0 - m * (1.0 - shade) + inner_shadow * rim` → 1.0 outside, `shade` inside.

**Finding 3 — cut-out halo on dark sets.** The alpha matte keeps the *original* light backdrop's
colour in its semi-transparent fringe. Composited onto emerald velvet, a white macramé product showed
a bright halo (vision rating 3/10). Fix: `imaging.decontaminate_edges()` replaces fringe RGB with the
Gaussian-weighted average of nearby opaque product colour. Rating for the same image rose to 8/10,
and an independent judge reported "edges are clean without a bright white halo".

**Matters.** None of these were visible in a code review — they only appeared by rendering, measuring
pixel statistics, and looking at the result. Two of the three produced *silently* wrong output (no
exception, no failure) — exactly the class of bug that the SOP-before-code rule and the numeric gate
exist to catch.

**Also learned.** Three stacked black layers compound multiplicatively
(`1-(1-a)(1-b)(1-c)`): combining a 0.28 ambient + 0.68 contact + 0.45 cast shadow darkened the floor
by ~87 % and produced a "dark rectangular block". They are now tuned to ~30–40 % at the contact point.

---

## F14 — Scene validation by rendering, not by assumption

**Method.** Render all four sets at full 4K with the product composited, crop the floor region at
native resolution, and read the result back.

**Outcome.**
| set | judge rating after the fixes | notes |
|-----|------------------------------|-------|
| marble | "natural veining, soft shadow, faint mirrored reflection of the feathers — convincing" | glossy floor reflection visible |
| velvet | 8/10 | "edges clean without a bright white halo"; bloom deliberately disabled — on a dark set a bloom reads as a cut-out |
| travertine | 9/10 realism / 8/10 premium | "distinct arched niche… believable shadow grounding the object" |
| botanical | 8/10 | "clear floor line, soft shadow consistent with overhead lighting" |

**Remaining, by design.** The product keeps its *own* lighting, so on a moody set its illumination
does not match the set's key light. Relighting it would mean regenerating product pixels, which
invariant I1 forbids. This is the documented trade-off of the identity guarantee — not a defect.

