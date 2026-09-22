# 07 — Web UI (`app.py`, Layer 0)

## Goal
The only user-facing surface: upload → progress → 4-up results → download / recreate, plus a
Settings screen for the LLM connection with a live **Test connection** button.

## Routes
| Route | Method | Purpose |
|-------|--------|---------|
| `/` | GET | Upload page + product name/category + scene preview |
| `/generate` | POST | multipart `image`, `product_name`, `product_category` → `{job_id}` (202, immediate) |
| `/status/<job_id>` | GET | `{state, stage, progress, outputs[], error}` — polled by the browser |
| `/result/<job_id>/<n>` | GET | one watermarked JPEG (2160×3840) |
| `/download/<job_id>.zip` | GET | ZIP of the 4 finals + manifest |
| `/recreate/<job_id>` | POST | new job, same source, seed+1 → `{job_id}` |
| `/settings` | GET | Settings screen (LLM connection, brand, background provider) |
| `/settings` | POST | save settings (key never returned to the browser) |
| `/settings/test` | POST | **Test connection** against the configured LLM text model |
| `/healthz` | GET | liveness |

## Invariants
- **W1** API key lives server-side only; responses return a masked form (`AQ.A…XUmA`).
- **W2** `/generate` returns immediately; the pipeline runs on a **background thread** (4 stages take time).
- **W3** job state = plain dict guarded by a `threading.Lock`.
- **W4** uploads validated (ext, size ≤ 15 MB, long edge ≥ 1000 px) **before** any API spend.
- **W5** the web layer never mutates pixels; all pixel work stays in `tools/`.

## Progress model
`queued → running(segment) → running(generate ×4) → running(composite) → running(canvas) → running(watermark) → running(verify) → done | failed`
Progress is a 0–100 integer updated by `run_job.py` via a callback.

## Recreate
The results screen has a **Recreate** button → `POST /recreate/<job_id>` → new job id, same stored
source, `seed+1`, so the user gets a fresh aesthetic set without re-uploading.
