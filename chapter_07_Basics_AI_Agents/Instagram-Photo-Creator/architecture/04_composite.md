# 04 — Composite (`composite.py`)

## Goal
Stand the **original** product pixels on the styled set, with the grounding cues that make a shot
read as a photograph rather than a paste-up.

## Inputs
`product_rgba.png` (de-contaminated), `mask.png`, `bg_<scene>.png`, `job.seed`, scene spec.

## Placement — `placement()`
- The product is anchored by its **base**, not its centre: `base_y = scene.place.bottom_y * H`.
  With `horizon` sitting a little above `bottom_y`, the product reads as standing on the floor.
- Horizontally centred; `left = (W - layer.width) // 2`.
- `build_product_layer()` scales **uniformly** to `width_pct * W`, additionally clamped so the
  product clears the top margin (`TOP_MARGIN = 0.09 H`). No non-uniform resize (I4/D4).

## Composite order (this order matters)
```
1. cast shadow      silhouette of the product, blurred, thrown AWAY from the key light
                    (shadow.offset — e.g. +x when the light is upper-left)
2. ambient pool     very wide, very soft ellipse straddling the base line
3. contact shadow   tighter, darker ellipse at the base — the cue that it is touching the surface
4. reflection       mirrored bottom slice of the product, alpha-faded downward, blurred
                    (glossy sets only)
5. halo             optional very subtle bloom behind the product (light sets only; on the dark
                    emerald set a bloom reads as a cut-out glow, so it is disabled)
6. product          the ORIGINAL pixels, alpha-composited last
```

Because the product is drawn last, every pixel inside its opaque core is byte-identical to the
source — which is exactly what `verify.py` checks.

## Grounding strengths
Set per scene via `shadow: {opacity, contact, ambient, offset}` — e.g. `marble` throws right
(light is upper-left), `velvet` throws left (light is on the right). Three stacked black layers
compound (`1-(1-a)(1-b)(1-c)`), so they are tuned to reach ~30–40 % darkening at the contact point,
not 80 %.

## Edge cases
| Case | Handling |
|------|----------|
| Product taller than the space above the base | scale down until it clears `TOP_MARGIN` |
| Sparse product bottom (fringe, strings) | reflection is naturally faint — physically correct |
| Dark floor (velvet) | shadow opacity raised and the floor lifted so the shadow can actually read |
| Overlay running past the canvas edge | `paste_blend` crops the overlay instead of raising |

## Output
`(composed RGB at exact canvas size, placement)` — the placement feeds `verify.py`.
