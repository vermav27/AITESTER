# 05 — Canvas & Watermark (`enforce_canvas.py`, `watermark.py`)

## Goal
Guarantee the exact 9:16 4K frame, then stamp one small brand watermark.

## enforce_canvas.py
1. Assert the composed image is already 2160×3840 (the composer builds at final size).
2. If it is not: **cover**-scale (`max(W/w, H/h)`) → LANCZOS → **center-crop** to (2160, 3840).
3. Never stretch (non-uniform resize forbidden, invariant I4).
4. Assert `img.size == (2160, 3840)`; raise `JobFailed("CanvasMismatch")` otherwise.

## watermark.py
1. Draw `@meraki.by.ankita` (from Settings → brand.handle) as a **small** mark.
2. Size: the rendered **text width ≈ 15 % of canvas width** (`size_pct`, clamped to 3–35 %), which works
   out to a font of roughly 3.5–4 % of the width (≈ 75–85 px at 2160). Opacity ≈ 55 %.
   The font size is **binary-searched** to hit the target width, so the mark stays proportional whatever
   the handle's length.
3. Position: bottom-right with a 4 % margin (configurable: `bottom-right|bottom-center|bottom-left`).
4. Render on an RGBA overlay with a faint shadow for legibility on light and dark scenes, then composite.
5. The watermark is the **only** text we add (D2 satisfied: no other overlays).

## Edge cases
| Case | Handling |
|------|----------|
| Font file missing | fall back to `PIL.ImageFont.load_default()` scaled, or the bundled DejaVu path |
| Background busy in that corner | shadow + slight opacity keeps it legible without shouting |

## Output
`final_<scene>.png` (2160×3840, watermarked)
