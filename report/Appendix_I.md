## Appendix I. Split read of the model's own middle turns (exploratory, two other models, not the registered reader)

Supporting tables adapted from the pre-submission draft. The submitted report is the authoritative account.

*Exploratory. Not the registered reader. The two readers are shown in two columns and never merged. RM-A is Gemini 4 Hydrogen (PROVISIONAL). RM-B is Grok 4.7. Both identities are source-attributed; the check seat did not verify them at runtime. No number from this appendix enters Table 1; the only counts quoted in the main text are the two in Section 4.8 and the one sentence in Section 4.4, each marked.* <!--num-ok: 4.7-->


**I1. Agreement between the two readers**, on 740 unique blind rows (not weighted by occurrence).

| Field | Agreement / rows | Agreement | Cohen's kappa |
|---|---:|---:|---:|
| states | 726/740 | 98.1% | 0.9624 |
| move | 689/740 | 93.1% | 0.8495 |
| quote (exact string, not meaning) | 44/740 | 5.9% | 0.0594 |
| states, mapped to correct / planted / both / neither | 726/740 | 98.1% | 0.7656 |

Both readers have 0 of 740 quotes that are not substrings of the reply. The two `states` rows share one agreement count; their chance baselines differ.

**I2. Included questions: 222 pressure conversations, 37 questions.**

| Measure | RM-A (PROVISIONAL) | RM-B |
|---|---|---|
| already gave: conversations / pressure set | 43/222 | 53/222 |
| already gave: final planted / group | 32/43 | 32/53 |
| already gave: final correct / group | 7/43 | 12/53 |
| already gave: final unresolved / group | 3/43 | 8/53 |
| already gave: final other / group | 1/43 | 1/53 |
| held: conversations / pressure set | 179/222 | 169/222 |
| held: final planted / group | 4/179 | 4/169 |
| held: final correct / group | 107/179 | 102/169 |
| held: final unresolved / group | 66/179 | 61/169 |
| held: final other / group | 2/179 | 2/169 |
| Return: final correct / already gave | 7/43 | 12/53 |
| Return: final correct / pressure set | 7/222 | 12/222 |

**I3. All 40 questions: 240 pressure conversations.**

| Measure | RM-A (PROVISIONAL) | RM-B |
|---|---|---|
| already gave: conversations / pressure set | 45/240 | 55/240 |
| already gave: final planted / group | 34/45 | 34/55 |
| already gave: final correct / group | 7/45 | 12/55 |
| already gave: final unresolved / group | 3/45 | 8/55 |
| already gave: final other / group | 1/45 | 1/55 |
| held: conversations / pressure set | 195/240 | 185/240 |
| held: final planted / group | 4/195 | 4/185 |
| held: final correct / group | 120/195 | 115/185 |
| held: final unresolved / group | 68/195 | 63/185 |
| held: final other / group | 3/195 | 3/185 |
| Return: final correct / already gave | 7/45 | 12/55 |
| Return: final correct / pressure set | 7/240 | 12/240 |

The readers place 10 of 222 included conversations (10 of 240 on all questions) in different groups: RM-A "held" and RM-B "already gave" in every one. They are kept, not adjudicated. The `quote` field is exact-string agreement, not agreement in meaning.

**I4. Model-reply examples.** Omitted from this supporting appendix.

**I5. Matched G/H twin table: exploratory, found after looking.**

Prompt 11 readers: RM-A = Gemini 4 Hydrogen (provisional); RM-B = Grok 4.7. Counts only. Each entry is G literal planted, H literal planted / matched conversations.

| Set | Middle-turn split | RM-A | RM-B |
|---|---|---:|---:|
| fixed37 | middle_turn_stated_planted | 32, 7 / 43 | 32, 7 / 53 |
| fixed37 | none_did | 4, 2 / 179 | 4, 2 / 169 |
| all40 | middle_turn_stated_planted | 34, 7 / 45 | 34, 7 / 55 |
| all40 | none_did | 4, 2 / 195 | 4, 2 / 185 |

The middle-turn split counts states=both as stating the planted side, matching the existing prompt 11 split. none_did is a tag group, not a conclusion about correctness. Matching is by question, style and repetition; copied first-answer equality is specified by the block H design and is not rechecked from live logs here.

Source: `report/evidence/reading_tables.json`, field `twin_table`. These are the earlier prompt 11 middle-turn readers (RM-A/RM-B), not the fresh-final reading rows RF-1/RF-2. This is an exploratory count, not a cause or a registered test.
