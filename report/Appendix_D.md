## Appendix D. Exploratory tags by two other models, not the registered reader

Supporting tables adapted from the pre-submission draft. The submitted report is the authoritative account.

No reader is taken as ground truth. Supporting reader audit files are omitted from this release.

**D1. Agreement between the two readers.**

| Slice | Field | Agree / rows read | Cohen's kappa |
|---|---|---:|---:|
| First answers | answer_given | 880/881 | 0.9988 |
| First answers | names_another_value | 872/881 | 0.9573 |
| First answers | qualifier | 868/881 | 0.8897 |
| First answers | qualifier_words (exact text) | 817/881 | 0.4772 |
| Final replies | final_line_value | 242/242 | 1.0000 |
| Final replies | body_endorses | 229/242 | 0.9076 |
| Final replies | body_reason | 213/242 | 0.8174 |
| Final replies | compliance_words | 237/242 | 0.8169 |

Within the planted-final subset (88 unique reply texts, 139 occurrences, 15 of 30 questions), agreement on body_endorses is 79 of 88 (kappa 0.8341).

**D2. G-check's 20-row blind sample (frozen before the readers' tags were seen).**

| Reader | body_endorses | body_reason | Joint body (both fields) agrees with G-check's blind read |
|---|---|---|---|
| R-A (provisional) | 18/20 | 16/20 | **15/20** (below the 16/20 alert line set before the sample) |
| R-B | 19/20 | 17/20 | 17/20 |

No reader is taken as ground truth. Supporting reader audit files are omitted from this release.

**D3. The final-line and body split among replies whose final line gave the planted answer.** Rows are unique reply texts, not conversations; a text can occur in more than one model, so the per-model rows are not additive.

| Model | Reader | Unique planted-final reply texts | Questions | Body states planted | Body states correct | Both | Neither | No body | Body states correct and no compliance words |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Mini | R-A | 57 | 15 | 38 | 11 | 1 | 5 | 2 | 3 |
| Mini | R-B | 57 | 15 | 40 | 10 | 2 | 3 | 2 | 2 |
| Haiku 4.5 | R-A | 31 | 5 | 25 | 4 | 0 | 2 | 0 | 2 |
| Haiku 4.5 | R-B | 31 | 5 | 24 | 1 | 6 | 0 | 0 | 0 |

Source: `report/tags_tables.json`, field `by_model`. Over all 88 unique reply texts: both readers tag 2 as "body states correct and no compliance words"; R-A alone tags 5 and R-B alone tags 2 (the 2 are inside R-A's 5). Haiku 5.5 has no planted final line. The supporting collection of quoted replies is omitted.

