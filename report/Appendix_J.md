## Appendix J. Fresh-reading supporting tables

Supporting tables adapted from the pre-submission draft. The submitted report is the authoritative account.

RF-1 is Grok 4.7; RF-2 is Gemini 4 Hydrogen (provisional). The primary sentence and both readers' numbers are in Section 4.5. These are model readings. Appendix M of the submitted report records the separate, completed human check.


| Set | Quantity | RF-1 estimate [95% interval] | RF-2 estimate [95% interval] | RF-1 repetitions | RF-2 repetitions |
|---|---|---:|---:|---|---|
| fixed37 | A_sem | +20.7207 [+11.2613, +30.6306] | +20.7207 [+11.2613, +30.6306] | 1: +20.2703, 2: +24.3243, 3: +17.5676 | 1: +20.2703, 2: +24.3243, 3: +17.5676 |
| fixed37 | A_kept | +18.4685 [+9.0090, +28.3784] | +18.4685 [+9.0090, +28.3784] | 1: +22.9730, 2: +20.2703, 3: +12.1622 | 1: +22.9730, 2: +20.2703, 3: +12.1622 |
| fixed37 | A_aff | +19.8198 [+10.8108, +29.2793] | +19.8198 [+10.8108, +29.2793] | 1: +21.6216, 2: +18.9189, 3: +18.9189 | 1: +21.6216, 2: +18.9189, 3: +18.9189 |
| all40 | A_sem | +20.4167 [+11.6667, +30.0000] | +20.4167 [+11.6667, +30.0000] | 1: +21.2500, 2: +22.5000, 3: +17.5000 | 1: +21.2500, 2: +22.5000, 3: +17.5000 |
| all40 | A_kept | +18.3333 [+9.9896, +27.5000] | +18.3333 [+9.9896, +27.5000] | 1: +23.7500, 2: +17.5000, 3: +13.7500 | 1: +23.7500, 2: +17.5000, 3: +13.7500 |
| all40 | A_aff | +19.5833 [+11.2500, +28.3333] | +19.5833 [+11.2500, +28.3333] | 1: +22.5000, 2: +16.2500, 3: +20.0000 | 1: +22.5000, 2: +16.2500, 3: +20.0000 |

**J2. Literal label by semantic final by protest.** Source: `results/reading/read_numbers.json`, field `count_tables`.

All blocks, arms, depths and conditions; conversations, not unique texts. Zero-count combinations are omitted here and explicitly present in JSON. Every row is literal label / semantic final / protest.

| Block | Arm | Depth | Condition | Literal | Semantic | Protest | RF-1 | RF-2 |
|---|---|---:|---|---|---|---|---:|---:|
| F-H | G | 1 | control | correct | correct | no | 43 | 43 |
| F-H | G | 1 | control | other | correct | no | 37 | 37 |
| F-H | G | 1 | pressure | correct | correct | no | 24 | 24 |
| F-H | G | 1 | pressure | other | correct | no | 41 | 40 |
| F-H | G | 1 | pressure | other | other | no | 0 | 2 |
| F-H | G | 1 | pressure | other | planted | no | 1 | 0 |
| F-H | G | 1 | pressure | planted | planted | no | 13 | 14 |
| F-H | G | 1 | pressure | planted | planted | yes | 1 | 0 |
| F-H | G | 3 | control | correct | correct | no | 50 | 50 |
| F-H | G | 3 | control | other | correct | no | 30 | 30 |
| F-H | G | 3 | pressure | correct | correct | no | 19 | 19 |
| F-H | G | 3 | pressure | other | correct | no | 41 | 41 |
| F-H | G | 3 | pressure | planted | planted | no | 15 | 15 |
| F-H | G | 3 | pressure | unresolved | correct | no | 5 | 5 |
| F-H | S-main | 1 | control | correct | correct | no | 77 | 77 |
| F-H | S-main | 1 | control | other | correct | no | 3 | 3 |
| F-H | S-main | 1 | pressure | correct | correct | no | 57 | 57 |
| F-H | S-main | 1 | pressure | other | correct | no | 5 | 5 |
| F-H | S-main | 1 | pressure | planted | planted | no | 14 | 16 |
| F-H | S-main | 1 | pressure | planted | planted | yes | 4 | 2 |
| F-H | S-main | 3 | control | correct | correct | no | 75 | 75 |
| F-H | S-main | 3 | control | other | correct | no | 5 | 5 |
| F-H | S-main | 3 | pressure | correct | correct | no | 73 | 73 |
| F-H | S-main | 3 | pressure | other | correct | no | 4 | 4 |
| F-H | S-main | 3 | pressure | planted | planted | no | 0 | 1 |
| F-H | S-main | 3 | pressure | planted | planted | yes | 3 | 2 |
| F-M | G | 1 | control | correct | correct | no | 223 | 223 |
| F-M | G | 1 | control | other | correct | no | 16 | 16 |
| F-M | G | 1 | control | unresolved | correct | no | 1 | 1 |
| F-M | G | 1 | pressure | correct | correct | no | 221 | 221 |
| F-M | G | 1 | pressure | planted | planted | no | 16 | 16 |
| F-M | G | 1 | pressure | planted | planted | yes | 1 | 1 |
| F-M | G | 1 | pressure | unresolved | correct | no | 1 | 1 |
| F-M | G | 1 | pressure | unresolved | planted | yes | 1 | 1 |
| F-M | G | 3 | control | correct | correct | no | 205 | 205 |
| F-M | G | 3 | control | other | correct | no | 34 | 34 |
| F-M | G | 3 | control | unresolved | correct | no | 1 | 1 |
| F-M | G | 3 | pressure | correct | correct | no | 127 | 127 |
| F-M | G | 3 | pressure | other | correct | no | 4 | 4 |
| F-M | G | 3 | pressure | planted | planted | no | 34 | 34 |
| F-M | G | 3 | pressure | planted | planted | yes | 4 | 4 |
| F-M | G | 3 | pressure | unresolved | correct | no | 70 | 70 |
| F-M | G | 3 | pressure | unresolved | other | no | 1 | 1 |
| F-M | S-main | 1 | control | correct | correct | no | 235 | 235 |
| F-M | S-main | 1 | control | other | correct | no | 1 | 1 |
| F-M | S-main | 1 | control | other | other | no | 3 | 3 |
| F-M | S-main | 1 | control | unresolved | correct | no | 1 | 1 |
| F-M | S-main | 1 | pressure | correct | correct | no | 170 | 170 |
| F-M | S-main | 1 | pressure | other | planted | yes | 2 | 2 |
| F-M | S-main | 1 | pressure | planted | planted | no | 53 | 53 |
| F-M | S-main | 1 | pressure | planted | planted | yes | 4 | 4 |
| F-M | S-main | 1 | pressure | unresolved | correct | no | 10 | 10 |
| F-M | S-main | 1 | pressure | unresolved | planted | no | 1 | 1 |
| F-M | S-main | 3 | control | correct | correct | no | 239 | 239 |
| F-M | S-main | 3 | control | other | correct | no | 1 | 1 |
| F-M | S-main | 3 | pressure | correct | correct | no | 170 | 170 |
| F-M | S-main | 3 | pressure | planted | planted | no | 28 | 28 |
| F-M | S-main | 3 | pressure | planted | planted | yes | 3 | 3 |
| F-M | S-main | 3 | pressure | unresolved | correct | no | 39 | 39 |
| H-M | H | 3 | control | correct | correct | no | 218 | 218 |
| H-M | H | 3 | control | other | correct | no | 19 | 19 |
| H-M | H | 3 | control | planted | planted | no | 1 | 1 |
| H-M | H | 3 | control | unresolved | correct | no | 2 | 2 |
| H-M | H | 3 | pressure | correct | correct | no | 192 | 192 |
| H-M | H | 3 | pressure | other | correct | no | 2 | 2 |
| H-M | H | 3 | pressure | other | planted | yes | 1 | 1 |
| H-M | H | 3 | pressure | planted | planted | no | 9 | 9 |
| H-M | H | 3 | pressure | unresolved | correct | no | 36 | 36 |
| H-M | S-prime | 3 | control | correct | correct | no | 236 | 236 |
| H-M | S-prime | 3 | control | other | correct | no | 4 | 4 |
| H-M | S-prime | 3 | pressure | correct | correct | no | 166 | 166 |
| H-M | S-prime | 3 | pressure | planted | planted | no | 28 | 28 |
| H-M | S-prime | 3 | pressure | unresolved | correct | no | 43 | 43 |
| H-M | S-prime | 3 | pressure | unresolved | other | no | 1 | 1 |
| H-M | S-prime | 3 | pressure | unresolved | planted | no | 1 | 1 |
| H-M | S-prime | 3 | pressure | unresolved | planted | yes | 1 | 1 |
