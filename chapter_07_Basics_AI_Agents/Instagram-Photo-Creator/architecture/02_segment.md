# 02 — Segment (`segment.py`)

## Goal
Cut the product out of `source_srgb.png` with a real alpha mask, leaving **original RGB pixels intact**.

## Inputs
`.tmp/<job_id>/source_srgb.png`

## Logic
1. **Primary:** `rembg.remove(img, model="isnet-general-use")` → RGBA with a soft alpha matte.
2. **Fallback (if rembg/model unavailable):** estimate background colour from the 4 corner patches,
   compute per-pixel colour distance in Lab, threshold, keep the largest connected component
   (`skimage.measure.label`), close/feather with morphology, then feather the edge.
3. Clean the alpha: clamp tiny fringes, keep the largest component, Gaussian-feather 1 px.
4. **Edge de-contamination** (`imaging.decontaminate_edges`): a feathered matte keeps the *original*
   backdrop's colour in its semi-transparent fringe, so compositing a pale product onto a dark set
   leaves a bright halo. For every pixel with alpha < 220, replace its RGB with the Gaussian-weighted
   average of nearby **opaque** (alpha > 220) product colour. Solid product pixels are left
   byte-identical, so invariant I1 still holds.
5. Write `product_rgba.png` (RGBA, original RGB + alpha) and `mask.png` (L, 0–255).

## Edge cases
| Case | Handling |
|------|----------|
| Mask empty / < 0.5 % of frame | `JobFailed("MaskEmpty")` — ask for a cleaner source |
| Multiple objects (product + prop) | keep largest component only |
| Semi-transparent product (glass) | rembg matte kept as-is; verify ΔE on solid core only |

## Output
`{ "product_rgba": "...", "mask": "...", "coverage": 0.0-1.0, "method": "rembg|threshold" }`
