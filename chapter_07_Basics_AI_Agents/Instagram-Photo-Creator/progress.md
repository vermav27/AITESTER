# progress.md — Work Log, Errors & Results

> **Project:** Instagram-Photo-Creator · **Convention:** newest entry on top.
> **Cadence:** log per 10-min tick during active work, and always at phase boundaries.
> **Legend:** ✅ done · 🔄 in progress · ❌ error/blocked · ⚠️ caveat · ⏭️ next

---

## 2026-09-22 · 14:20 IST — Revision: flat backdrops → styled luxury sets

**Phase:** ✨ Stylize (second pass, on user feedback)

**Feedback:** *"I donot want plain backgrounds in the edited images. It should be aesthetic, with some
good luxury setup, so that my product looks great and professional."*

### What was done
- ✅ New SOP first (Golden Rule): rewrote `architecture/03` (sets), `architecture/04` (grounding),
  `architecture/02` (de-contamination), `architecture/06` (opaque-core gate).
- ✅ New `tools/lib/textures.py` — procedural materials and atmosphere: `marble`, `strata` (travertine),
  `velvet`, `wood`, `plaster`, `arch_niche`, `dapple`, `blind_shadow`, `bokeh`, `glow`,
  `linear_light`, `cove_floor_light`, `reflection_fade`. All seeded and deterministic.
- ✅ `tools/lib/scenes.py` rewritten: the four scenes are now **layered sets**, each stacking wall
  material → cove → floor → architecture → light → vignette → grain, with per-scene `place`,
  `reflection`, `shadow` and `halo` specs.
  `studio/lifestyle/outdoor/gradient` → **`marble` (Polished Calacatta)**, **`velvet` (Emerald Velvet)**,
  **`travertine` (Travertine Atelier)**, **`botanical` (Botanical Salon)**.
- ✅ `tools/composite.py` rewritten for grounding: base-anchored placement, cast shadow thrown **away
  from each set's key light**, ambient pool, contact shadow, floor reflection, optional back-light
  halo, and a clipping-safe `paste_blend`.
- ✅ `tools/segment.py` — edge de-contamination (`imaging.decontaminate_edges`) to kill cut-out halos.
- ✅ `tools/verify.py` — the gate now takes the compositor's exact placement rect, measures ΔE on the
  **opaque core** (alpha ≥ 250) and SSIM on that core **eroded 3 px**.
- ✅ UI: scene list now shows each set's `blurb`; `scenes_public()` keeps the non-serialisable `build`
  callable out of the template.

### Errors / blockers (all found by rendering and measuring, all resolved)
- ❌ **Every set washed out to near-white.** `tint()` takes a 0–1 field; `glow()`/`linear_light()`
  passed 0–255, so the light layer saturated and `screen()` blew out the frame (velvet measured
  `[213,208,198]` instead of emerald). Fixed by normalising the strength. → F13-1
- ❌ **`arch_niche` painted everything outside the arch black** (`m * shade` is 0 where the mask is 0).
  Fixed to `1.0 - m*(1-shade) + rim`. → F13-2
- ❌ **Shape confusion throughout `textures.py`.** PIL `size` is `(width, height)`; several functions
  unpacked it as `(h, w)`, and `fbm` allocated `np.zeros(size)` instead of `(h, w)`. Fixed everywhere
  and documented on `grid()`/`fbm()`.
- ❌ **Bright cut-out halo on the velvet set** (judged 3/10). Cause: the feathered matte retains the
  *original* light backdrop's colour. Fixed with edge de-contamination → 8/10. → F13-3
- ❌ **Product floated / looked pasted.** The contact shadow was centred *above* the base line (behind
  the product) and the cast shadow barely escaped it. Rebuilt as ambient + contact + directional cast.
- ❌ **Over-corrected the shadows** — 0.28/0.68/0.45 stacked to ~87 % darkening, a "dark rectangular
  block". Re-tuned to ~30–40 % at the contact point.
- ❌ **`verify` reported ΔE 4.2 on a *faithful* composite** (a false failure that would have broken
  every real job). Two causes: the mask included the feathered edge, and the rect was rebuilt from a
  rounded centre — `round(112.5) == 112` while the compositor used `left = 113`, i.e. one pixel off.
- ❌ **`GET /` returned HTTP 500** after the rewrite: the scene dicts now hold a `build` **function`,
  and `{{ scenes | tojson }}` cannot serialise it. Fixed with `scenes_public()`.

### Results
- ✅ Full 4K job: **4/4 pass** — marble ΔE 0.057/SSIM 0.9989 · velvet 0.190/0.9997 ·
  travertine 0.051/0.9991 · botanical 0.059/0.9990. Job ≈ **27 s**, ZIP ≈ 7.8 MB.
- ✅ Self-test: **23/23** (`tools/selftest.py --network`), including two new checks — the four sets are
  materially distinct (min 16×16 thumbnail L1 0.053) and glossy sets actually reflect the product
  (peak Δ 24 below the base).
- ✅ Independent visual review of the four full-resolution sets: marble "convincing", velvet 8/10,
  travertine 9/10 realism, botanical 8/10.
- ✅ Browser flow re-verified over CDP: 4 cards, all `pass`, 2160×3840 thumbnails, ZIP link, Recreate
  starts a new job.

### Known limitation (by design)
The product keeps its **own** lighting, so on a moody set it is not relit to match the key light.
Relighting would mean regenerating product pixels, which invariant I1 forbids. Documented in F14.

### Next (⏭️)
1. With an image-quota key: Settings → Background provider → `gemini` for model-generated sets.
2. Optional: 1080×1920 companions for direct IG upload (4K masters are kept).

---

## 2026-09-22 · 13:30 IST — Phases 1–4: built, run, and live-tested end-to-end

**Phase:** 🏗️ Blueprint → ⚡ Link → ⚙️ Architect → ✨ Stylize (all four in one pass)

### What was done
- ✅ **Phase 1 (Blueprint):** locked schemas in `LLM.md` §3 (input, manifest, web API, **new §3.5 settings schema**); added invariants **I10** (one watermark) and rule **R7**; rewrote D2 so the brand watermark is the one allowed mark; recorded ADR-8/ADR-9.
- ✅ **Phase 2 (Link):** probed the supplied key live. `x-goog-api-key` authenticates (Bearer does not). Text OK; **all image models 429 with free-tier limit 0** (F10). Built `tools/check_env.py` as the standing handshake gate and `tools/llm_client.py` (Gemini adapter + `test_connection` + `describe_image_model`).
- ✅ **Phase 3 (Architect):** wrote 8 Layer-1 SOPs in `architecture/` *before* any code (Golden Rule). Built the Layer-3 tools — `ingest`, `segment`, `generate_backgrounds`, `composite`, `enforce_canvas`, `watermark`, `verify`, `export` — plus Layer-2 `run_job.py` (fixed routing order, progress reporting).
- ✅ **Phase 4 (Stylize):** Flask Layer-0 `app.py` + Jinja `base/index/settings` + hand-written CSS/JS. Upload → background thread → `/status` polling → 4-up 9:16 gallery with per-image ΔE/SSIM badges → per-image download + **Download all (ZIP)** + **Recreate**. Settings screen with LLM connection + live **Test connection**.

### Key decisions made
- **Local procedural backgrounds are the v1 default** (ADR-8). The key's image quota is 0, so a deterministic PIL renderer supplies the four scenes; `background_provider = auto` probes Gemini once and falls back. Gemini needs no code change to take over later.
- **Recreate = new job, seed+1, same source** — verified: job `f6f52270a00f` (seed 42) and its recreate `5f044a60f417` (seed 43) produce byte-different outputs.
- **Watermark is drawn after canvas enforcement**, sized by **text width ≈ 15 % of the canvas** (font binary-searched to hit that width), and `verify.py` fails the job if its bbox is missing.
- **`/settings/test` never persists the key it tests** — it passes an override into the adapter, so testing a bad key cannot clobber a working one.

### Errors / blockers (all resolved)
- ❌ **429 on every image model** → the fundamental blocker → resolved by ADR-8 (local renderer); Gemini retained behind the adapter. Documented in F10.
- ❌ `NameError: verify_tool` in `run_job.py` → missing import → added `from tools import verify as verify_tool`.
- ❌ `IndexError: invalid index to scalar variable` in `verify.py` → SSIM return values unpacked in the wrong order (`s, _` instead of `_, s`) → fixed.
- ❌ **Watermark was 25 % of the canvas wide** (545 px) → `size_pct` sized the *font*, not the *text* → `watermark.py` now binary-searches the font size to hit a target **text width** (default 15 %); also removed Pillow's deprecated `Image.fromarray(..., "RGB")` mode argument across `tools/lib/imaging.py`.
- ❌ `/settings/test` **persisted** whatever key it was given → a bad test key would overwrite a good one → added a non-persisting `override` path through `llm_client`.
- ⚠️ A stray non-ASCII glyph slipped into `scenes.py` (`"#b07d४2"`) → corrected to `"#b07d42"`.
- ⚠️ Two of my own self-test assertions were wrong (compared the trimmed product against the *untrimmed* source aspect; verified drifted pixels against themselves) → both corrected; see T-11 / T-15.

### Results
- ✅ Full pipeline on `Input/Test.JPG`: **4/4 pass** — 2160×3840, ΔE 0.74–0.85 (gate ≤3.0), SSIM 0.980–0.986 (gate ≥0.95). Segment coverage 21.97 % via rembg `isnet-general-use`. Job ≈ 21 s.
- ✅ HTTP flow verified with curl: `POST /generate` → 202 with job id; `/status` walked `ingest → segment → generate → composite → done`; `/result/…/1` returned a 1.88 MB JPEG; `/download/<id>.zip` returned 8.37 MB with 4 JPEGs + `manifest.json`.
- ✅ `POST /recreate/<id>` → new job at seed 43. `POST /settings/test` → `{"ok":true,"model":"gemini-3.6-flash","reply":"CONNECTION_OK","latency_ms":2299}`.
- ✅ Security: `/settings` renders the key **masked** (`AQ.A…XUmA`); the raw key never appears in a response body (grep-checked).
- ✅ UI rendered in headless Chrome and reviewed visually (upload page and settings page both 9/10 polish; no unstyled elements). Server live at `http://127.0.0.1:5001` (port 5001 — macOS AirPlay owns 5000).
- ✅ **`tools/selftest.py --network` → 20/20 checks pass** (ingest contracts, matte fidelity, determinism, canvas, watermark sizing, gate pass *and* fail-closed, config, live link).
- ✅ **Full browser flow driven over CDP**: file attached → preview shown → stages advanced → **4 cards rendered, all `pass`** with 2160×3840 thumbnails → ZIP link present → **Recreate** started a new job. `TESTPLAN.md` records **44/44 checks**.

### Next (⏭️)
1. If an image-quota key is available: set Settings → Background provider → `gemini` to swap in model-generated backdrops.
2. Optional: 1080×1920 companion exports for direct IG upload (4K masters are kept).

---

## 2026-09-22 · 12:41 IST — Protocol 0: Discovery answered

**Phase:** 🟢 Protocol 0 (Initialization) → Blueprint

### What was done
- ✅ Recorded the user's Discovery answers:
  - **Q2 Backend:** Gemini 2.5 Flash Image (`gemini-2.5-flash-image-preview`)
  - **Q3/Q4 Interface:** **Web UI** — upload in, preview + ZIP download out
  - **Q1 Reel style:** 4 **independent** scenes (also stitch into one reel)
- ✅ Updated `task_plan.md`: Phase 2 now targets the Gemini handshake; Phase 3 adds `run_job.py` + `app.py`; Phase 4 rewritten as a real web UI spec; Discovery table filled.
- ✅ Updated `findings.md`: F8 marked resolved, added **F9** (Flask chosen over Streamlit; background-thread + polling because a 4-call Gemini job is long-running; upload validation before any API spend).
- ✅ Updated `LLM.md`: status, web-layer contract, and the ADR for the interface.
- ✅ Marked the backend decision final in `findings.md` F3.

### Key decisions made
- **Flask, not Streamlit.** The pipeline is already Python functions; Streamlit's rerun-on-interaction model fights a multi-minute, multi-stage job that must stream progress.
- **Job is async.** `/generate` starts a background thread and returns a `job_id`; the browser polls `/status/<job_id>`. Reason: 4 sequential Gemini calls are tens of seconds — must not block the HTTP request.
- **Validate before spending.** Mime + ≥1000px long edge + ≤15MB gate runs before the first paid API call.

### Errors / blockers
- ⚠️ Still no `GEMINI_API_KEY` in `.env` → Phase 2 handshake untested.
- ⚠️ No sample product photo yet → segmentation + scene recipes unvalidated against a real subject.
- ⏸️ Halt still in force: BLAST requires the **Blueprint + Schema** to be signed off before `tools/` code. Both drafts are ready.

### Results
- Discovery complete (4/5 questions closed; only the first test photo's product category remains).
- No pixel output yet — by design.

### Next (⏭️)
1. **User:** sign off the blueprint (`task_plan.md`) and schema (`LLM.md` §3).
2. **User:** provide `GEMINI_API_KEY` and one raw product photo.
3. **Me:** lift the halt → Phase 2 Link handshake → Phase 3 build.

---

## 2026-09-22 · 12:39 IST — Protocol 0: Project Memory init

**Phase:** 🟢 Protocol 0 (Initialization)
**Actor:** System Pilot

### What was done
- ✅ Read `BLAST.md` → adopted B.L.A.S.T. protocol + A.N.T. 3-layer architecture.
- ✅ Read `PromptUsed.md` → confirmed Prompt 1 = Protocol 0 only; Prompt 2 is a *different* project (Jira→test-plan) and is out of scope here.
- ✅ Extracted the North Star: `1 raw product photo → 4 edited Instagram photos, 9:16, 4K, color/identity unchanged`.
- ✅ Created `task_plan.md` (phases, goals, checklists, Discovery questions).
- ✅ Created `findings.md` (F1–F8: architecture decision, backends, segmentation, upscaling, verification math, curl requests).
- ✅ Created `LLM.md` (constitution: schemas, rules, invariants).
- ✅ Created this `progress.md`.

### Key decision made
Discarded the naive "prompt the model to re-render the product" approach. Chose the **masked-composite pipeline**: the product's pixels are **never regenerated** — they are cut out with an alpha mask and **pasted back** over an AI-generated background. Identity/color preservation becomes a math guarantee (findings F2). Verification gate: ΔE2000 ≤ 3.0 and SSIM ≥ 0.95.

### Errors / blockers
- ❌ **BLOCKED (by design):** BLAST Protocol 0.2 forbids writing any `tools/` script until (a) Discovery answered, (b) schema signed off, (c) blueprint approved. → **No code written yet. Correct.**
- ⚠️ No source image uploaded yet → cannot even dry-run segmentation.
- ⚠️ Backend unknown (Q2 unanswered) → Phase 2 (Link) cannot start.

### Results
- 4/4 memory files exist. Project is initialized and **deliberately halted**.

### Next (⏭️) — needs the user
1. Answer Discovery Q1–Q5 (task_plan §3).
2. Upload 1 raw product photo (also tells us the product category).
3. Say which image-edit backend/keys to use.
→ Then I lift the halt and start Phase 1 proper (lock schema + write the 4 scene recipes), no coding until sign-off.

---

## Template for the next entry

```
## YYYY-MM-DD · HH:MM IST — <phase> · <task>
Phase: ...
### What was done
- ✅ ...
### Errors
- ❌ <exact error text / status code> → <what I tried> → <resolution>
### Results
- <measured outcome; include ΔE / SSIM / resolution when relevant>
### Next (⏭️)
- ...
```

---

## Change log (compressed)
| Timestamp | Phase | Event | Status |
|-----------|-------|-------|--------|
| 2026-09-22 14:20 | Stylize (rev 2) | Flat backdrops → 4 styled luxury sets; edge de-contamination; grounding; gate measured on the opaque core. 4/4 pass at ΔE ≈0.05 | ✅ |
| 2026-09-22 13:30 | Phases 1–4 | Built + ran the whole system; 4/4 images pass the gate; HTTP flow, recreate and LLM test verified | ✅ |
| 2026-09-22 12:41 | Protocol 0 → Blueprint | Discovery answered (Gemini + Web UI + 4 independent scenes); docs updated | ✅ |
| 2026-09-22 12:39 | Protocol 0 | Created task_plan / findings / progress / LLM | ✅ |
