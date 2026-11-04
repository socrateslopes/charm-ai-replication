# Scoring of the AI-assisted replay

Scripts that score the runs in `execution/results/` against the answer keys
(protocol Section 9). Re-run them after any change to the alias tables:

```bash
python3 experiment/scoring/score_a.py          # Task A -> results/taskA-*.csv
python3 experiment/scoring/summarize_a.py      # micro-averages and error taxonomy
python3 experiment/scoring/score_b.py          # Tasks B0 and B1 -> results/taskB-*.csv
```

| File | Content |
|---|---|
| `questionnaires.py` | The developers' answers to Q3–Q9, transcribed from the five questionnaires (answer key, item level) |
| `reference.py` | Parser of the reconciled characterization in `execution-b/B0-inputs/characterization` (answer key, relation level) |
| `score_a.py` | Normalization, alias tables (the protocol's "alias table") and Task A metrics |
| `summarize_a.py` | Micro-averages across services and the error taxonomy |
| `score_b.py` | Task B answer keys, the researcher's issue-to-category matching, and Task B metrics |
| `results/` | Generated CSVs |

Service names here are the real ones; the manuscript uses the public names
(payin-processor = Payin Processor, credit-card-processor = Credit Card Processor, agents-commissions =
Agents Commissions, bank-interface = Bank Interface, payout-processor = Payout Processor).

## Results (final, 2026-10-01)

The runs of payin-processor, agents-commissions and B1 repeated in `execution-rerun/` replace
the first-execution runs (protocol Section 11). Add `--first-execution` to any
script to score the first execution instead (output in
`results/first-execution/`).

### Task A (5 runs)

Item level, against the questionnaires (micro-averaged):

| Dimension | Questionnaire | Agent | Matched | P | R | F1 |
|---|---|---|---|---|---|---|
| Operations (Q3) | 118 | 149 | 117 | 0.79 | 0.99 | 0.88 |
| Sync calls (Q4) | 56 | 79 | 55 | 0.70 | 0.98 | 0.81 |
| Topics (Q5+Q6) | 109 | 135 | 101 | 0.75 | 0.93 | 0.83 |
| Data sources (Q7) | 12 | 21 | 11 | 0.52 | 0.92 | 0.67 |
| Module components (Q9) | 13 | 35 | 12 | 0.34 | 0.92 | 0.50 |

The 123 extra items: 35 possibly unused, legacy or test; 31 platform or
infrastructure; 20 granularity or module boundary; 5 naming or method
mismatch; 32 other items not in the questionnaire. Per-item list:
`results/taskA-item-diffs-classified.csv`.

Relation level, against the reconciled characterization (72 relations):
agent recall 0.85, precision 0.55; questionnaires recall 0.99, precision 1.00.
The agent matched the reconciled value in both answers that reconciliation
had corrected.

Evidence: 1,189 of 1,192 snapshot citations exist; 129 citations point to
other repositories of the organization. Time: 11–20 min per service, 82 min in
total.

Run-to-run variation (first execution vs rerun): payin-processor nearly identical;
agents-commissions found 8 vs 3 of its 8 invoking services and labeled its internal
queues at a coarser granularity in the rerun.

### Tasks B0 and B1

| Metric | B0 | B1 (rerun) | B1 (first, discarded) |
|---|---|---|---|
| Patterns present: precision | 8/10 | 10/14 | 10/13 |
| Patterns present: recall (15) | 8/15 | 10/15 | 10/15 |
| Recall weighted by participants | 0.64 | 0.76 | 0.76 |
| Suggested patterns recommended (10) | 4/10 | 4/10 | 7/10 |
| … suggested by ≥2 participants (8) | 4/8 | 4/8 | 7/8 |
| Problem categories found (3) | 3/3 | 3/3 | 3/3 |
| Claims with all evidence valid | 24/24 | 34/34 | 36/36 |
| Time (min) | 4 | 9 | 11 |

Answer key: the revised counts of the dissertation (protocol Section 11,
deviation 12). With the pre-registered counts (`score_b.py --preregistered-key`,
`results/preregistered-key/`): precision 7/10 and 9/14, recall 7/14 and 9/14,
weighted recall 0.65 and 0.75, suggested patterns recommended 4/9 and 4/9.

Pending checks and deviations: protocol Section 11.
