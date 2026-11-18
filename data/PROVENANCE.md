# Data provenance

The source_archives.json file lists the original generation archives by block, SHA-256, byte count and conversation count. Each archive identifier uses the first 16 hexadecimal characters of its full SHA-256. The original archives are held outside this package. The H design refers to three source archives by the same identifiers.

The rows directory contains the analysis rows. The replies directory contains saved visible turns. The verifier checks the join between these files, hashes the saved turn text, and recomputes the literal answer and format labels. The reading_labels.jsonl file contains the labels used by the reading analyses.

The questions_fresh.jsonl file retains the frozen bytes used to build the fresh-question arms, including the original writer attribution. The arm exports retain the original object hashes. Their metadata uses release labels.

The H builder pinned the whole original F arm file. Its digest is recorded in arms_H.json under pinned_input_hashes. The packaged F arm export has its own file digest in the package manifest. The verifier checks the three sets of pinned arm objects and rebuilds the first-run and fresh-question objects.
