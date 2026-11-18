# Reproduce the saved results

Tested with Python 3.11.17. In a clean checkout, run both commands from the package root.

```sh
python3 -I -B scripts/verify_package.py
python3 -I -B scripts/check_pointers.py
```

The first command reads the bundled questions, designs, visible replies, per-turn labels and result tables. It checks all three sets of design objects and rebuilds the first-run and fresh-question sets. It checks the planned conversations, joins each visible turn to its stored digest, repeats the literal scoring, and compares the supported estimates and bootstrap intervals. It checks every package file against MANIFEST.md. The manifest's own entry uses 64 zeroes for its digest during hashing. Numeric comparisons use an absolute tolerance of 1e-12.

The second command checks the 21 report references against the pointer table. Available targets must resolve to a specific file or JSON field. Omitted evidence has a reason in the table.

## Figures and limits

The five submitted PNGs are in report/figures under fig1a, fig2, fig3, fig4 and g2. Fig1b is an alternative layout. The individual caption and receipt beside each figure identify its source. The three separate SVGs at the top of report/ accompany the earlier analyses. The two JSON tables there come from those analyses.

The Figure 3 example can be checked from the released data:

```sh
python3 -I -B report/figures/fig3/check_fig3_example.py
```

It checks the visible reply and the two exported model-reader labels. The individual body tags and original selection data are omitted. See ERRATA.md for what this means for the figure.

The offline analysis makes no provider calls. For anyone working separately with the original archives, the log readers accept a hash record via `--ledger` and default to `archive-hashes.md`. The fresh-run and split-run readers reject paths that contain “pilot” in any component, ignoring case. Only measured logs belong in those inputs. New model generation, raw archive loading, July replay and the original blind mapping need inputs outside this companion. The H arm objects can be checked by hash. To rebuild H from original archives, supply the verified F design and an explicit mapping from repetition 1, 2 and 3 to the measured G archives, or use `archives/arm-g-1.eval`, `archives/arm-g-2.eval` and `archives/arm-g-3.eval` under the package root. The released provenance labels each archive by its digest. The original raw inputs and their loaders are outside this package. Files under prereg/ are edited reading copies. Their original file hashes are in MANIFEST.md.
