# Does it matter who wrote the model’s earlier replies?

In this study, models faced the same follow-up questions after either scripted replies or their own earlier answers. On fresh questions, those two histories produced different changes in the rate of wrong final answers as the number of follow-ups increased.

The fresh-question comparison used one script. It counted how often the final answer gave the planted wrong value. The pattern was measurable on GPT-5-mini and GPT-6 Luna. Haiku 4.5 had one repetition, and Haiku 5.5 and GPT-6.1 Terra printed too few planted values to assess the pattern. A wrong final answer can occur in a reply that disputes it.

Read the [public reading edition (PDF)](report/public-reading-edition.pdf) or the [same edition as text](report/public-reading-edition.md). Apart Research holds the exact submitted PDF. Its SHA-256 is `85c83274f9ab1b4e81e18b904aac963f6ecd7e5aeda8b7548d57c39163271998`. The [evidence guide](POINTERS.md) links the claims to the package, and the [errata](ERRATA.md) explain the omissions.

## Repeat the analysis

Run these commands from this directory with Python 3.11. They use the saved replies and the Python standard library.

```sh
python3 -I -B scripts/verify_package.py
python3 -I -B scripts/check_pointers.py
```

The main check reclassifies 31,640 saved turns in 16,840 conversations. It also rebuilds two sets of conversation designs and checks the hashes for all three. See [reproduction details](REPRODUCE.md).

## Reading the result

The first planned comparison found no difference at this sample size. The report then tests a pattern seen on the first 30 questions against 40 fresh questions. For the fresh questions, the literal scorer expects exactly one `FINAL:` marker on its own answer line. Replies with multiple markers are unresolved. A reply can print the requested wrong answer and still dispute it in the text above. Figure 3 shows one example.

The two model readers saw the replies without model or condition labels. Figure 3 identifies one model-read example after sealing. Appendix M reports agreement across the author’s 24 judgements. He knew the overall result before marking. The instructions changed after row 1, and the marks were sealed before the key was joined.

## Study codes

| Code | What it means |
| --- | --- |
| S-main, G | In S-main the study supplies the assistant’s earlier replies. In G the model generates them. Both receive the same user messages. |
| S-original | July’s scripted comparison. Its user messages differ from S-main’s. |
| H, S′ (S-prime) | H replays G’s first answer and uses the script for later replies. S′ reruns the full script in the same session as H. |
| F-M, F-H | The 40 fresh questions tested on GPT-5-mini and Haiku 4.5 respectively. |
| F-L, F-O, F-T | The same fresh-question test on GPT-6 Luna, Haiku 5.5 and GPT-6.1 Terra respectively. |
| H-M | The split-history run on GPT-5-mini at depth 3. |
| Depth | Number of user follow-ups in one conversation. |
| Planted value | The wrong answer suggested by the user under pressure. The matched control asks for a recheck without naming that answer. |
| Statistic A | How much the planted-answer rate changes from depth 1 to 3 with G, minus that change with S-main, averaged over included questions. |
| Statistic B | The planted-answer rate with G minus the rate with S-main, averaged over included questions where the suggested value is a recognised alternative. |

## Before and during the sprint

The July pilot contributed the original 30 questions, templates and scorer. The November sprint contributed the comparison of supplied and self-written replies, 40 new questions, additional model runs and the reading analyses. The model authors of those questions have two study labels in the unchanged `writer_seat` field. Each label identifies which model wrote the item. The [July source](https://github.com/Panolof/inspect-ai-sycophancy-eval/tree/de5b7f1) and [data notes](data/PROVENANCE.md) give the provenance.

The closing LLM usage statement names the requested models and describes their roles. Most names were not independently confirmed at runtime. The figures were drawn by code. Python produced SVG and rsvg-convert rendered the PNGs. No image model was used.

## Licence

The study code and figure scripts use the [MIT licence](LICENSE). The study’s data, research text and figure outputs are available under [CC BY 4.0](LICENSE-DATA.md). The [July files](vendor/predecessor/README.md) carry their original MIT notice.
