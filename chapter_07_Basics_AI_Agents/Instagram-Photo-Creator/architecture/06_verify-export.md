# 06 — Verify & Export (`verify.py`, `export.py`)

## Goal
Gate every image numerically before it is allowed into `output/`, then write deliverables + manifest.

## verify.py checks (per image)
| Check | Rule | Fail action |
|-------|------|-------------|
| Canvas | `size == (2160, 3840)` | `JobFailed("CanvasMismatch")` |
| Product present | mask coverage ≥ 0.5 % | `JobFailed("MaskEmpty")` |
| Colour fidelity | ΔE2000 ≤ 3.0 between source product pixels and the output, **measured on the opaque core only (alpha ≥ 250)** | `JobFailed("ColorDrift")` |
| Structure | SSIM ≥ 0.95 on the same opaque core | `JobFailed("StructureDrift")` |
| Watermark | watermark bbox differs from the un-watermarked composite | `JobFailed("WatermarkMissing")` |

Because the product is **pasted from the original** (I1), ΔE is ≈ 0 by construction; the gate exists
to catch an accidental grade or a wrong paste. Bias: **fail closed** — a missing image beats a wrong image.

> **Why the opaque core, not the whole mask.** A feathered edge pixel (alpha ≈ 128) is *designed* to
> blend with the backdrop, so its output colour is legitimately part background. Measuring it would
> grade the set, not the product. Restricting the gate to alpha ≥ 250 measures exactly the invariant
> we care about: the product's own pixels came through untouched.

## export.py
- Write `output/<job_id>/NN_<scene>.jpg` — JPEG quality 95, `subsampling=0` (4:4:4).
- Write `output/<job_id>/manifest.json` (schema in `LLM.md` §3.2): job id, timings, backend,
  source sha256, per-image scene/metrics/verdict, seed, errors.
- Write `output/<job_id>/<job_id>.zip` (4 finals + manifest) for "Download all".

## Edge cases
| Case | Handling |
|------|----------|
| Any image fails verify | job → `failed`; **nothing** is written to `output/` |
| Recreate | new `job_id`, seed+1, same source; previous output kept |
