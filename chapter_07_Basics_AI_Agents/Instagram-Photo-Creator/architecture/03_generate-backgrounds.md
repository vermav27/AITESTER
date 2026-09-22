# 03 — Generate Backgrounds (`generate_backgrounds.py`)

## Goal
Produce four **empty** styled 9:16 sets, one per scene. The product is never drawn here (I2).
Each set is a *room*, not a wash: a wall material, a floor material, a cove between them,
architectural detail, directional light and atmosphere.

## Scenes (fixed ids)
| id | Set | Build |
|----|-----|-------|
| `marble` | **Polished Calacatta** | book-matched marble wall + glossy marble floor, cove, raking daylight from the upper-left, floor sheen |
| `velvet` | **Emerald Velvet** | deep emerald velvet drapes in vertical folds + velvet floor, single warm raking light from the right, deep shadow |
| `travertine` | **Travertine Atelier** | bedded travertine wall with an **arched niche**, stone floor, diagonal window light + faint blind shadow |
| `botanical` | **Botanical Salon** | mottled sage lime-plaster wall with leaf dapple + defocused greenery bokeh, oak plank floor, airy top light |

Each scene declares: `horizon`, `place`, `reflection`, `shadow`, `halo`, `prompt` and a `build` fn.

## The build pipeline (`tools/lib/textures.py`)
Every set is composed from seeded primitives — all deterministic, all at half resolution then
upscaled, with full-resolution grain applied last:

```
material(wall) ─┐
material(floor) ─┴─ cove stack at `horizon`     ← _stack()
   → cove_floor_light     darken + sheen below the horizon
   → arch_niche / dapple / blind_shadow            (scene-specific architecture & shadow patterns)
   → screen(glow) / screen(linear_light)           directional key light
   → vignette → grain(seed)                        atmosphere + film grain
```

| Primitive | Produces |
|-----------|----------|
| `marble` | two crossing vein families warped by turbulence + two fbm washes (avoids visible repetition) |
| `strata` | horizontal bedding bands + pitting (travertine/limestone) |
| `plaster` | broad mottling, almost no pattern (lime wash) |
| `velvet` | vertical folds catching a raking light |
| `wood` | fine grain lines + subtle plank tone breaks |
| `arch_niche` | rounded-top recess as a multiply mask (`shade` inside, rim at the edge) |
| `dapple` / `blind_shadow` | leaf-shadow and venetian-blind multiply masks |
| `bokeh` | defocused highlights, screened over the base |
| `glow` / `linear_light` | radial light pool / directional wash |

> **Normalisation trap (fixed):** `tint(field, c_dark, c_light)` expects a **0–1** field. Passing a
> 0–255 light value makes the layer blow out to white and `screen()` washes the whole set — this is
> how the first build lost all its contrast.

## Providers
- **local (default):** the procedural pipeline above. Offline, free, deterministic.
- **gemini (optional):** `gemini-3.1-flash-image` text-to-image with `aspectRatio: 9:16`,
  `responseModalities:["IMAGE"]`, using the scene's `prompt`.
- **auto:** probe the image model once; use Gemini if it has quota, else fall back to local and
  record the reason.

## Edge cases
| Case | Handling |
|------|----------|
| Gemini 429 / no image quota | `auto` falls back to local, records `auto → local (QuotaExceeded)` in the manifest |
| Model returns < 9:16 | cover-scale to the canvas; else local fallback |
| Returned image contains a product | discarded: backgrounds must be empty |
| Explicitly forced `gemini` with no quota | fails loudly with the model's message — the user chose it |

## Output
`bg_<scene>.png` × 4 (RGB, exactly 2160×3840)
