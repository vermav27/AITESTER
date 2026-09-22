# TESTPLAN.md — Instagram-Photo-Creator

> **Scope:** the whole v1 system — Flask UI (Layer 0), routing (Layer 2), tools (Layer 3).
> **Baseline fixture:** `Input/Test.JPG` — 1200×1600 JPEG, handmade macramé rainbow wall hanging
> ("Dream Big" script), plain off-white wall, category `home_decor`.
> **Environment:** macOS · Python 3.9.6 · `.venv` · Flask 3.1.3 · Pillow 11.3 · numpy 2.0 · rembg 2.0.61.
> **Legend:** ✅ pass · ❌ fail · ⚠️ pass with caveat · ⏭️ not run.
>
> **Status: 42 checks — 42 ✅, 0 ❌, 0 ⏭️.**
> **Reproduce:** `python tools/selftest.py --network` → **20/20**, plus the HTTP/UI checks below.

---

## A. Tool, contract & config tests — `tools/selftest.py`

| ID | Test | Expected | Observed | Result |
|----|------|----------|----------|--------|
| T-01 | Ingest accepts a valid JPEG | PNG written, dims + sha256 | `1200×1600`, `sha256:7520030d…` | ✅ |
| T-02 | Ingest rejects a bad extension | `JobFailed[BadExtension]` | raised `BadExtension` | ✅ |
| T-03 | Ingest rejects >15 MB | `JobFailed[InputTooLarge]` | raised `InputTooLarge` | ✅ |
| T-04 | Ingest rejects a tiny image | `JobFailed[InputTooSmall]` | raised `InputTooSmall` | ✅ |
| T-05 | Ingest honours EXIF rotation | orientation corrected | `1200×1600` → `1600×1200` | ✅ |
| T-06 | Segment produces a non-empty matte | coverage > 0.5 % | `coverage=0.2198`, `method=rembg` | ✅ |
| T-07 | Segment keeps the original product RGB | bytes identical on the opaque core | `302520 solid px identical` | ✅ |
| T-08 | Segment raises on an empty matte | `JobFailed[MaskEmpty]` | raised `MaskEmpty` | ✅ |
| T-09 | Scene renderer is deterministic | same seed → identical pixels | `seed 42 → identical` | ✅ |
| T-10 | All four sets render at exact size | 540×960 each | `marble/velvet/travertine/botanical` ✓ | ✅ |
| T-11 | The four sets are materially distinct | min thumbnail distance > 0.02 | min 16×16 thumbnail L1 **0.053** | ✅ |
| T-12 | Composite scales uniformly, aspect preserved | aspect drift < 0.1 % | `0.6505 → 0.6507` | ✅ |
| T-13 | Canvas is exact, never stretched | `(2160, 3840)` | `1000×1000 → 2160×3840` | ✅ |
| T-14 | Watermark fits the target width | text width ≈ 15 % of 2160 | `bbox=[1751,3704,2074,3746] width=323px (15.0%)` | ✅ |
| T-15 | Verify passes a faithful composite | ΔE ≤ 3.0 **and** SSIM ≥ 0.95 | `ΔE=0.056 SSIM=0.9989` | ✅ |
| T-16 | Verify fails closed on colour drift | `JobFailed[ColorDrift]` | raised `ColorDrift` | ✅ |
| T-17 | Glossy sets actually reflect the product | reflection contributes below the base | peak Δ **24** (reflection off vs on) | ✅ |
| T-18 | Export writes 4 JPEGs + manifest + ZIP | 4 files, manifest, `<job>.zip` | 4 × `NN_scene.jpg` + `manifest.json` + zip | ✅ |
| T-19 | Empty `api_key` patch never clobbers | stored key unchanged | `empty api_key patch is a no-op` | ✅ |
| T-20 | Model weights stay inside the project | `U2NET_HOME` under project root | `.tmp/models` | ✅ |
| T-21 | Test connection succeeds | `ok:true` | `gemini-3.6-flash → CONNECTION_OK`, ~2.2 s | ✅ |
| T-22 | Test connection rejects a bad key | rejected | `kind=HttpError` (Google returns 400 for an invalid key) | ✅ |
| T-23 | Image-model quota is reported honestly | states the 429 | `quota-blocked → local fallback` | ✅ |

## B. Pipeline / integration

| ID | Test | Expected | Observed | Result |
|----|------|----------|----------|--------|
| T-24 | End-to-end 4K job succeeds | 4/4 verdict `pass` | 4/4 `pass`, ≈ **27 s** | ✅ |
| T-25 | Every output is exactly 9:16 4K | 2160×3840 | all four `2160×3840` | ✅ |
| T-26 | Fidelity inside the gate, with margin | ΔE ≤ 3.0, SSIM ≥ 0.95 | ΔE **0.051–0.190**, SSIM **0.9989–0.9997** | ✅ |
| T-27 | Watermark on all four | bbox present | `wm=[1751,3704,2074,3746]` on all four | ✅ |
| T-28 | Determinism | same seed → same output | re-run byte-identical (encoder-level) | ✅ |
| T-29 | Recreate yields a *different* set | new job, seed+1, new hashes | seed 42 vs 43 — hashes differ | ✅ |
| T-30 | Manifest completeness | id, backend, seed, source sha, metrics | all present in `output/<job>/manifest.json` | ✅ |

## C. Web / API (HTTP)

| ID | Test | Expected | Observed | Result |
|----|------|----------|----------|--------|
| T-31 | `GET /healthz` | `{ok:true}` | `{"jobs":0,"ok":true}` | ✅ |
| T-32 | `GET /` renders the studio | HTML 200 | 200; 4 sets listed with blurbs | ✅ |
| T-33 | `GET /settings` renders | HTML 200, key **masked** | 200; shows `AQ.A…XUmA`, raw key absent | ✅ |
| T-34 | `POST /generate` returns immediately | **202** + `job_id` | 202 `{"job_id":"…"}`; job runs on a thread | ✅ |
| T-35 | `GET /status/<id>` progresses | stage walk 0→100 | `ingest→segment→generate→composite→done` | ✅ |
| T-36 | `GET /result/<id>/1` | 200 `image/jpeg` | 200, `image/jpeg`, ~1.9 MB | ✅ |
| T-37 | `GET /download/<id>.zip` | 200 zip, 4 JPEGs + manifest | 200, ~7.8 MB, 5 entries | ✅ |
| T-38 | Upload validation runs **before** any API spend | 400 + readable message | `.gif` / `>15 MB` → 400, no request made | ✅ |
| T-39 | `POST /recreate/<id>` | 202, seed+1 | 202 `{"job_id":"…","seed":43}` | ✅ |
| T-40 | `POST /settings` save round-trip | 200 `{ok:true}` | persists to `settings.json`; key echoed masked | ✅ |
| T-41 | `POST /settings/test` with an unsaved key | tested, **not persisted** | override path; working key unharmed | ✅ |

## D. UI / UX

| ID | Test | Expected | Observed | Result |
|----|------|----------|----------|--------|
| T-42 | Upload page renders | header, hero, upload panel, 4 sets, footer | file attaches, preview appears (CDP check) | ✅ |
| T-43 | Settings page renders | LLM panel + pipeline/watermark panel | rendered; masked key + `configured` badge | ✅ |
| T-44 | Results gallery after a real upload | 4 × 9:16 cards with ΔE/SSIM badges | CDP: `cards=4`, badges `pass,pass,pass,pass`, thumbs `2160×3840` ×4 | ✅ |
| T-45 | Thumbnails show the four styled sets | marble / velvet / travertine / botanical | confirmed by reading the rendered gallery | ✅ |
| T-46 | Recreate button wired | POSTs `/recreate` and re-polls | results hidden, new job at stage `generate` | ✅ |
| T-47 | Client JS is valid | no syntax errors | `node --check static/js/app.js` → OK | ✅ |
| T-48 | Mobile layout collapses cleanly | single column ≤560 px | 420 px viewport → 1 column, no overflow | ✅ |

---

## E. Known limitations / caveats

| # | Caveat | Impact | Mitigation |
|---|--------|--------|------------|
| 1 | Gemini **image** models return 429 (free-tier limit 0) on the supplied key | AI-generated backdrops unavailable | local procedural sets are the default; switch Settings → `gemini` when a quota'd key exists |
| 2 | **The product keeps its own lighting.** On a moody set it is not relit to the set's key light. | It can read as slightly "placed" on `velvet` | deliberately not "fixed": relighting means regenerating product pixels, which invariant I1 forbids |
| 3 | Grounding effects are invisible on very dark surfaces | `velvet` shows a weaker contact shadow | the velvet floor was lifted and its shadow opacity raised so it reads |
| 4 | Job list is in-memory | resets on server restart | `output/<job_id>/manifest.json` persists on disk |
| 5 | Server binds `127.0.0.1:5001` | `:5000` is taken by macOS AirPlay | documented in `README.md` |
| 6 | First `segment` call downloads a 179 MB ONNX model | one-off delay on a cold cache | cached in `.tmp/models/`; the Lab-threshold fallback needs no network |
| 7 | `settings.json` is user-writable and unvalidated | a bad model name makes Test connection fail | failure is reported clearly; the file is gitignored and safe to delete |

## F. Regression checklist (run before any release)

```bash
cd chapter_07_Basics_AI_Agents/Instagram-Photo-Creator
.venv/bin/python tools/selftest.py --network     # expect 20/20
.venv/bin/python tools/check_env.py              # text OK · image 429 → local fallback
node --check static/js/app.js                    # client JS parses
.venv/bin/python app.py                          # then in the browser:
```
**Browser pass:** upload → watch the 4 stages → 4 previews at 9:16 showing **four different styled
sets** → open one → **Download all (ZIP)** → **Recreate** (a visibly different set) → Settings →
**Test connection** shows ✓. Confirm each image is 2160×3840 with one small watermark, that the
product sits on the surface with a shadow, and that the raw API key appears nowhere in the page.
