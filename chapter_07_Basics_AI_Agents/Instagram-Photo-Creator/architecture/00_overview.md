# 00 — Architecture Overview (Layer 1 SOP)

> **Project:** Instagram-Photo-Creator · **Protocol:** B.L.A.S.T. + A.N.T. 3-layer
> **Golden Rule:** if logic changes, edit the SOP before the code.

## Goal
One uploaded product photo → **4** aesthetic, professionally-composed Instagram photos, each
**2160×3840 (9:16, 4K)**, each carrying one small `@meraki.by.ankita` watermark, downloadable
individually and as a ZIP, and reproducible on demand (**Recreate**).

## The 3 layers
```
Layer 0  Web UI (app.py, Flask)     Upload → start job → poll status → preview → download/recreate.
                                     User surface only. Never does pixel work. Never sees the API key.
Layer 1  architecture/ (this dir)   Markdown SOPs: goals, inputs, tool logic, edge cases. No code.
Layer 2  Navigation (tools/run_job) Routes data between atomic tools; owns job state + scene order.
Layer 3  tools/*.py                 Atomic, deterministic Python. One responsibility each.
```

**Dependency rule:** Layer 3 tools never import each other (except shared `tools/lib/`).
Layer 2 wires Layer 3. Layer 0 calls Layer 2. Layer 1 documents everything.

## Pipeline (fixed order)
```
ingest → segment → generate_backgrounds(×4 scenes) → composite(×4) → enforce_canvas → watermark → verify → export
```

## Architectural invariants
| # | Invariant | Enforcement |
|---|-----------|-------------|
| I1 | Product RGB pixels are **never regenerated**; they are cut out (alpha) and pasted back | `segment.py` + `composite.py`; `verify.py` fails if ΔE > 3.0 |
| I2 | Model generation is sandboxed to the **background only** | `generate_backgrounds.py` emits an empty 9:16 scene |
| I3 | Every image passes a numeric gate before export | `verify.py` (size, mask coverage, ΔE) |
| I4 | Canvas is exact 2160×3840; cover-scale → center-crop; never stretch | `enforce_canvas.py` asserts final size |
| I5 | Determinism: fixed seeds, no hidden state | seed recorded in `manifest.json` |
| I6 | Secrets only in `.env` / `settings.json`; never in responses or logs | `config.py` masks the key; `.gitignore` |
| I7 | Intermediates in `.tmp/<job_id>/`; deliverables in `output/<job_id>/` | `run_job.py` |
| I8 | Web layer is async: `/generate` returns `job_id`, browser polls `/status` | background thread + lock |

## Deviation from the original blueprint (recorded 2026-09-22)
The draft `LLM.md` assumed **Gemini 2.5 Flash Image** would synthesize the *backgrounds*.
Live testing proved the supplied key has **free-tier image quota = 0** for every
`*-image` model (HTTP 429). Therefore v1 generates the 4 backdrops with a **deterministic
procedural renderer** (`tools/lib/scenes.py`), while keeping the Gemini adapter in place so a
key with image quota can be selected in **Settings → Background provider = gemini** without
touching any other tool. This *strengthens* I1/I2 (the product is never model-touched) and keeps
the pipeline fully offline-capable.
