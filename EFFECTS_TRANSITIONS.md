# Effects to Transition and Idle Mapping

This file documents the stable API key contract. Each key defines a pair:
1. Transition effect used in xfade.
2. Idle/post-transition style used while the image is on screen.

Current renderer behavior for each clip:
1. Resolve key (`effect_key_00` ... `effect_key_49`) to a profile.
2. Apply profile visual preset (`Internal Effect`).
3. Apply profile idle style (pan/zoom rhythm + polish).
4. Join clips with profile transition.
5. Apply global final polish after all transitions.

- Public effect keys: 50 (`effect_key_00` to `effect_key_49`)
- Transition modes configured: 50
- Idle style variants: 5 (`idle_soft`, `idle_warm`, `idle_cool`, `idle_punch`, `idle_calm`)

## Mapping Table (Stable Public Keys)

| # | Effect Key | Internal Effect | Transition | Idle Style |
|---|---|---|---|---|
| 0 | effect_key_00 | simple_fit | fade | idle_soft |
| 1 | effect_key_01 | warm_grade | fadeblack | idle_warm |
| 2 | effect_key_02 | cool_grade | fadewhite | idle_cool |
| 3 | effect_key_03 | high_contrast | fadegrays | idle_punch |
| 4 | effect_key_04 | soft_contrast | wipeleft | idle_calm |
| 5 | effect_key_05 | grayscale_soft | wiperight | idle_soft |
| 6 | effect_key_06 | grayscale_contrast | wipeup | idle_warm |
| 7 | effect_key_07 | sepia_soft | wipedown | idle_cool |
| 8 | effect_key_08 | sepia_deep | slideleft | idle_punch |
| 9 | effect_key_09 | negative | slideright | idle_calm |
| 10 | effect_key_10 | mirror_h | slideup | idle_soft |
| 11 | effect_key_11 | rotate_cw | slidedown | idle_warm |
| 12 | effect_key_12 | rotate_ccw | smoothleft | idle_cool |
| 13 | effect_key_13 | rotate_soft | smoothright | idle_punch |
| 14 | effect_key_14 | blur_soft | smoothup | idle_calm |
| 15 | effect_key_15 | blur_medium | smoothdown | idle_soft |
| 16 | effect_key_16 | blur_strong | circlecrop | idle_warm |
| 17 | effect_key_17 | sharpen_soft | rectcrop | idle_cool |
| 18 | effect_key_18 | sharpen_strong | circleopen | idle_punch |
| 19 | effect_key_19 | vignette_soft | circleclose | idle_calm |
| 20 | effect_key_20 | vignette_medium | vertopen | idle_soft |
| 21 | effect_key_21 | vignette_hard | vertclose | idle_warm |
| 22 | effect_key_22 | noise_soft | horzopen | idle_cool |
| 23 | effect_key_23 | noise_medium | horzclose | idle_punch |
| 24 | effect_key_24 | hue_shift_warm | dissolve | idle_calm |
| 25 | effect_key_25 | hue_shift_cool | pixelize | idle_soft |
| 26 | effect_key_26 | saturation_boost | radial | idle_warm |
| 27 | effect_key_27 | saturation_reduce | distance | idle_cool |
| 28 | effect_key_28 | brightness_boost | diagtl | idle_punch |
| 29 | effect_key_29 | brightness_reduce | diagtr | idle_calm |
| 30 | effect_key_30 | gamma_warm | diagbl | idle_soft |
| 31 | effect_key_31 | gamma_cool | diagbr | idle_warm |
| 32 | effect_key_32 | film_grain | hlslice | idle_cool |
| 33 | effect_key_33 | cinematic | hrslice | idle_punch |
| 34 | effect_key_34 | portrait_pop | vuslice | idle_calm |
| 35 | effect_key_35 | soft_pastel | vdslice | idle_soft |
| 36 | effect_key_36 | teal_orange | hblur | idle_warm |
| 37 | effect_key_37 | retro_tint | zoomin | idle_cool |
| 38 | effect_key_38 | magenta_tint | fadefast | idle_punch |
| 39 | effect_key_39 | clarity | fadeslow | idle_calm |
| 40 | effect_key_40 | dream_glow | hlwind | idle_soft |
| 41 | effect_key_41 | noir_film | hrwind | idle_warm |
| 42 | effect_key_42 | sunset_pop | vuwind | idle_cool |
| 43 | effect_key_43 | arctic_pop | vdwind | idle_punch |
| 44 | effect_key_44 | vhs_soft | coverleft | idle_calm |
| 45 | effect_key_45 | fade_matte | coverright | idle_soft |
| 46 | effect_key_46 | clean_commercial | coverup | idle_warm |
| 47 | effect_key_47 | pastel_wash | coverdown | idle_cool |
| 48 | effect_key_48 | bold_magazine | revealleft | idle_punch |
| 49 | effect_key_49 | soft_skin | revealright | idle_calm |

## Notes

- Preferred client contract is `effect_key_00` ... `effect_key_49`.
- Direct internal effect names are still accepted for backward compatibility.
- Effects input supports three formats:
  - single string key: `"effects": "effect_key_01"` (auto-applies to all 10 clips)
  - one-item list: `"effects": ["effect_key_01"]` (auto-applies to all 10 clips)
  - ten-item list: `"effects": ["effect_key_00", ..., "effect_key_49"]`
