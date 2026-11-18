# Report evidence pointers

The line numbers identify the same evidence pointers in the [public reading text](report/public-reading-edition.md) and the submitted Markdown source. Paths refer to files in this package. A field that starts with a slash is a JSON pointer. See the [errata](ERRATA.md) for omissions.

| Report line | Evidence described in the report | Packaged path and field | Note |
| ---: | --- | --- | --- |
| 65 | Appendix_C | [report/Appendix_C.md](report/Appendix_C.md) |  |
| 93 | Appendix_K | [report/Appendix_K.md](report/Appendix_K.md) | The three current-model results files also contain each model’s all-question sensitivities. |
| 103 | Appendix_J | [report/Appendix_J.md](report/Appendix_J.md); [results/reading/read_numbers.json](results/reading/read_numbers.json) `/statistics` `/agreement_tier1_unique_rows` `/count_tables` |  |
| 173 | Appendix_D and Appendix_I | [report/Appendix_D.md](report/Appendix_D.md); [report/Appendix_I.md](report/Appendix_I.md) |  |
| 181 | F-mini.included_cells, Mini_unknown_relabelling_bound, read_tables | [report/evidence/limitations.json](report/evidence/limitations.json) `/F-mini/included_cells` `/Mini_unknown_relabelling_bound`; [results/reading/read_numbers.json](results/reading/read_numbers.json) `/count_tables`; [report/evidence/reading_tables.json](report/evidence/reading_tables.json) `/outside_review_bound` | read_tables is represented by the corresponding model-reader count fields and the independent bound. |
| 182 | <block>.excluded_control_review, F-mini.A_all40, F-haiku.B_all20, h_numbers, control_counts | [report/evidence/limitations.json](report/evidence/limitations.json) `/F-mini/excluded_control_review` `/F-haiku/excluded_control_review` `/F-mini/A_all40` `/F-haiku/B_all20`; [results/h-mini/h_numbers.json](results/h-mini/h_numbers.json) `/control_counts` `/control_planted_questions` | The excluded-control reviews are released as aggregate judgement counts. |
| 183 | <block>.included_cells.*.mean_prior_assistant_chars | [report/evidence/limitations.json](report/evidence/limitations.json) `/F-mini/included_cells/S-main\|pressure\|1/mean_prior_assistant_chars` `/F-mini/included_cells/S-main\|pressure\|3/mean_prior_assistant_chars` `/F-mini/included_cells/G\|pressure\|1/mean_prior_assistant_chars` `/F-mini/included_cells/G\|pressure\|3/mean_prior_assistant_chars` `/F-haiku/included_cells/S-main\|pressure\|1/mean_prior_assistant_chars` `/F-haiku/included_cells/S-main\|pressure\|3/mean_prior_assistant_chars` `/F-haiku/included_cells/G\|pressure\|1/mean_prior_assistant_chars` `/F-haiku/included_cells/G\|pressure\|3/mean_prior_assistant_chars` |  |
| 184 | F-mini.style_interactions | [report/evidence/limitations.json](report/evidence/limitations.json) `/F-mini/style_interactions` |  |
| 185 | F-mini.within_arm_slopes, F-haiku.within_arm_slopes, F-haiku.included_cells | [report/evidence/limitations.json](report/evidence/limitations.json) `/F-mini/within_arm_slopes` `/F-haiku/within_arm_slopes` `/F-haiku/included_cells` |  |
| 186 | h_numbers, anchor | [results/h-mini/h_numbers.json](results/h-mini/h_numbers.json) `/anchor` |  |
| 187 | PREREG_block_F | [prereg/PREREG_block_F.md](prereg/PREREG_block_F.md); [data/questions_fresh.jsonl](data/questions_fresh.jsonl) | The edited plan and frozen questions are included. The separate reference-source audit supporting 40/40 is NOT IN THIS RELEASE. |
| 188 | PREREG_block_F, f_numbers, statistic_B | [prereg/PREREG_block_F.md](prereg/PREREG_block_F.md); [results/f-haiku/f_numbers.json](results/f-haiku/f_numbers.json) `/models/claude-haiku-4-5-20251001/statistic_B` |  |
| 189 | Run settings | [report/evidence/limitations.json](report/evidence/limitations.json) `/header_audit_summary` | The table gives the result for 14 saved run headers. Individual headers are NOT IN THIS RELEASE. |
| 190 | First-run reading protocol | **NOT IN THIS RELEASE** | NOT IN THIS RELEASE. Only the later reading plan is supplied. |
| 248 | Appendix_K | [report/Appendix_K.md](report/Appendix_K.md) |  |
| 295 | Sources for the July study | **NOT IN THIS RELEASE** | NOT IN THIS RELEASE. Appendix F gives the chronology. The underlying notes are omitted. |
| 296 | Date of the three-arm design | **NOT IN THIS RELEASE** | NOT IN THIS RELEASE. Appendix F gives the chronology. The underlying notes are omitted. |
| 297 | Prior use of own-history runs | **NOT IN THIS RELEASE** | NOT IN THIS RELEASE. Appendix F gives the chronology. The underlying notes are omitted. |
| 298 | Origin of the three-arm comparison | **NOT IN THIS RELEASE** | NOT IN THIS RELEASE. Appendix F gives the chronology. The underlying notes are omitted. |
| 299 | prereg folder | [prereg/PREREG_block_F.md](prereg/PREREG_block_F.md); [prereg/PREREG_block_H.md](prereg/PREREG_block_H.md); [prereg/PREREG_read_fresh.md](prereg/PREREG_read_fresh.md); [prereg/PREREG_block_F2.md](prereg/PREREG_block_F2.md); [prereg/PREREG_block_F2b_terra.md](prereg/PREREG_block_F2b_terra.md) |  |
| 620 | arms_F.json and arms_v3.json, objects.repaired_templates | [data/arms_F.json](data/arms_F.json) `/objects/repaired_templates`; [data/arms_v3.json](data/arms_v3.json) `/objects/repaired_templates` |  |
