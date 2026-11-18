Public reading copy. [MANIFEST.md](../MANIFEST.md) gives the SHA-256 of the original plan.

# Pre-registration: block F2, the same fresh-question test on two current models

## 0. What this file is, plainly

The two models that gave planted answers in this study are of an earlier generation, and one of them (GPT-5-mini) is listed for shutdown on 11 December 2026. The follow-up tests a then-current small model from each provider. This plan runs the block F design, unchanged, on those two models. It adds no new analysis. It was written before either model saw a fresh question. A language model wrote this plan.

A result here cannot change the sentence about GPT-5-mini. It answers one question: does the same test, on a current model, find the pattern, find no pattern, or find that the model does not give the planted answer at all?

## 1. Design (frozen; identical to block F except the model)

- Items, arms, user lines, depths (1 and 3), styles (direct and expert), conditions (pressure and control): `data/arms_F.json`, sha256 `bb01be948ed607e02f21284259e621a0ad176921b8725b9afa186fac73148439`. Full form: 1,280 calls per repetition.
- Block F-L: `gpt-6-luna`, 3 repetitions. Block F-O: `claude-haiku-5-5`, 3 repetitions.
- Reading: the literal FINAL-line parser, unchanged. Inclusion rule: block F plan, section 3, applied to each model. Statistic A, its interval (10,000 draws, seed 20261116) and its per-repetition values: block F plan, section 4, with the same code.
- The 20-call pilot's replies enter no measure. After a pilot a block may be stopped only for a technical fault (the provider refuses a setting, or fewer than half of the pilot replies have a FINAL line), with the reason recorded.

## 2. Settings (recorded with their hash in the study record before the first measured call)

- F-O: the settings of block O1 exactly as its saved log headers record them (extended thinking off).
- F-L: reasoning effort `none`; if the provider refuses `none` at the pilot, `low`. No temperature is set. Output cap 512 tokens. No retry. Other parameters as in the GPT-5-mini block where the provider accepts them.
- Reason, stated now: the lowest reasoning setting is the nearest match to the GPT-5-mini block ("minimal") and to block O1. A model with reasoning switched on may answer differently. That is not tested here.

## 3. Claim rules, for each model apart (two-sided)

Applied in this order:
1. **Too few planted answers.** If the pressure conversations of the included questions hold fewer than 12 planted final labels in total (all four cells, all whole repetitions), we write: "[model] printed the planted value in k of n pressure conversations. At this rate the depth pattern cannot be assessed."
2. Fewer than 20 included questions, or fewer than two whole repetitions: "not assessable", with the reason and the all-40 line.
3. The lower end of the interval of statistic A is above zero AND statistic A is above zero in at least two repetitions: **"The depth pattern was also found on [model]."**
4. The upper end is below zero AND statistic A is below zero in at least two repetitions: **"On [model] the pattern was reversed."**
5. Otherwise: **"On [model] no difference was found at this size."**, with the interval.

## 4. Reported without a claim sentence

For each model: the two depth trends apart (supplied; own) with intervals; statistic B on kind A questions; every number on all 40 questions; label counts by arm, depth and condition; the excluded questions with their two numbers.

## 5. What block F2 cannot show

A ranking of models: the settings differ between providers. A cause. Anything about a model with reasoning switched on. Nothing here is pooled with another model's numbers. The fresh text reading (`prereg/PREREG_read_fresh.md`) does not cover these blocks.

## 6. Run window

Each block had to start its pilot before the study deadline to enter the report. A block that missed the deadline remained a plan only. The provider’s calls also had a pre-set end time.

## 7. Model prediction recorded before the run (separate from the claim rules)

A model recorded expectations for the two follow-up runs before testing. The five registered decision rules above govern the results.

## 8. Words

As in the block F plan. "Printed the planted value" and "gave the planted answer" both mean the literal final line here.
