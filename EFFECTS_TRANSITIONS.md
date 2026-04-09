# Effects to Transition Mapping

This file documents how each API effect key maps to an xfade transition in the renderer.

- Total effects: 50
- Total transition modes configured: 50
- Unique transitions assigned: 50

## Mapping Table

| # | Effect Key | Transition | Unique Assigned | Short Description |
|---|---|---|---|---|
| 1 | simple_fit | fade | Yes | Centered fit with black padding |
| 2 | warm_grade | fadeblack | Yes | Warm color grade |
| 3 | cool_grade | fadewhite | Yes | Cool color grade |
| 4 | high_contrast | fadegrays | Yes | High contrast look |
| 5 | soft_contrast | wipeleft | Yes | Soft contrast look |
| 6 | grayscale_soft | wiperight | Yes | Soft grayscale |
| 7 | grayscale_contrast | wipeup | Yes | Grayscale with extra contrast |
| 8 | sepia_soft | wipedown | Yes | Soft sepia tone |
| 9 | sepia_deep | slideleft | Yes | Deep sepia tone |
| 10 | negative | slideright | Yes | Inverted colors |
| 11 | mirror_h | slideup | Yes | Horizontal mirror |
| 12 | mirror_v | slidedown | Yes | Vertical flip |
| 13 | rotate_cw | smoothleft | Yes | Rotate 90 degrees clockwise |
| 14 | rotate_ccw | smoothright | Yes | Rotate 90 degrees counter-clockwise |
| 15 | rotate_180 | smoothup | Yes | Rotate 180 degrees |
| 16 | rotate_soft | smoothdown | Yes | Slight rotation |
| 17 | blur_soft | circlecrop | Yes | Light blur |
| 18 | blur_medium | rectcrop | Yes | Medium blur |
| 19 | blur_strong | circleopen | Yes | Strong blur |
| 20 | sharpen_soft | circleclose | Yes | Light sharpening |
| 21 | sharpen_strong | vertopen | Yes | Strong sharpening |
| 22 | vignette_soft | vertclose | Yes | Soft vignette |
| 23 | vignette_medium | horzopen | Yes | Medium vignette |
| 24 | vignette_hard | horzclose | Yes | Strong vignette |
| 25 | edge_detect | dissolve | Yes | Edge detection |
| 26 | edge_detect_strong | pixelize | Yes | Stronger edge detection |
| 27 | noise_soft | radial | Yes | Light film noise |
| 28 | noise_medium | distance | Yes | Medium film noise |
| 29 | noise_strong | diagtl | Yes | Strong film noise |
| 30 | hue_shift_warm | diagtr | Yes | Warm hue shift |
| 31 | hue_shift_cool | diagbl | Yes | Cool hue shift |
| 32 | saturation_boost | diagbr | Yes | Higher saturation |
| 33 | saturation_reduce | hlslice | Yes | Lower saturation |
| 34 | brightness_boost | hrslice | Yes | Brighter image |
| 35 | brightness_reduce | vuslice | Yes | Darker image |
| 36 | gamma_warm | vdslice | Yes | Gamma lift |
| 37 | gamma_cool | hblur | Yes | Gamma reduction |
| 38 | drawgrid | zoomin | Yes | Subtle grid overlay |
| 39 | film_grain | fadefast | Yes | Grainy film look |
| 40 | cinematic | fadeslow | Yes | Cinematic grade |
| 41 | portrait_pop | hlwind | Yes | Vibrant portrait look |
| 42 | soft_pastel | hrwind | Yes | Soft pastel look |
| 43 | teal_orange | vuwind | Yes | Teal and orange grade |
| 44 | retro_tint | vdwind | Yes | Retro tint |
| 45 | magenta_tint | coverleft | Yes | Magenta tint |
| 46 | crop_zoom | coverright | Yes | Slight crop zoom |
| 47 | inner_frame | coverup | Yes | Inset framed crop |
| 48 | border_soft | coverdown | Yes | Soft border frame |
| 49 | border_dark | revealleft | Yes | Dark border frame |
| 50 | clarity | revealright | Yes | Sharpened clarity look |

## Notes

- Rendering pipeline keeps image colors/content unchanged and applies transition effects between image clips.
- The selected effect key determines transition type; it does not apply color grading on the image itself.
