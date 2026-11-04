# From Developer Knowledge to AI Assistance: replication package

Material for the article *From Developer Knowledge to AI Assistance: Patterns
for Characterizing and Improving Microservice Architectures* (Lopes, Yoder and
Goldman; prepared for the Journal of Information Science and Engineering,
Special Issue on Patterns for AI-Driven Software Development). The article extends
the AsianPLoP 2026 paper "A tale of two worlds: using patterns from academia
and industry to improve microservices-based systems".

The study replays two steps of an industrial architecture characterization
with an LLM coding agent and compares the results with the validated outcomes
of the original study:

- **Task A:** the agent answers the CharM questionnaire for each of five
  services from a history-free snapshot of their code, configuration and
  deployment files.
- **Tasks B0 and B1:** given the reconciled characterization and the pattern
  catalog shown to the developers, an LLM identifies the patterns present,
  the architectural problems, and recommended patterns with drawbacks and
  priorities. B1 also receives the developers' comments and interview
  excerpts.

## What is here

| Folder | Content |
|---|---|
| `protocol/` | The study protocol: design, controls, answer keys, scoring rules, and every deviation (Section 11) |
| `prompts/` | The four prompts pasted into the agent (P0, A, B0, B1) |
| `instruments/` | CharM questionnaire, pattern catalog as shown to participants, system context given to Tasks B0 and B1, legend of the characterization tables |
| `guides/` | Step-by-step guides used to run the experiment and the rerun |
| `templates/` | Environment report and run-record templates |
| `tools/` | Snapshot, snapshot-rebuild, evidence-check and transcript-preparation scripts |
| `scoring/` | Scoring scripts for Tasks A and B and their documentation |
| `checks/` | Researcher checks: citation sample, drawbacks against the catalog's source book, spot-check of the drawback verdicts, patterns reported beyond the answer key |
| `results/` | Aggregate results: scores per service and dimension, relation-level comparison, error categories, evidence validity, Task B metrics |
| `SUPPLEMENT.md` | Details referred to in the article as Supplement S1 to S4 |

Services carry the fictitious names used in the article: Payin Processor,
Credit Card Processor (Pay In), Bank Interface, Agents Commissions and Payout
Processor (Pay Out). The company is referred to as REC.

## What is not here, and why

The system belongs to a company that did not authorize publishing its code
or its people's answers. The following stay private:

- the code snapshot and everything derived from it item by item: the agent's
  outputs, logs and chat exports, the evidence references, the snapshot and
  repository lists, and the item-level differences;
- the developers' questionnaire answers and written comments, and the
  interview transcripts;
- the reconciled characterization tables (they name internal services of
  other teams), summarized in `results/characterization-summary.csv`;
- the case-specific alias tables of the scorer, which map names from the
  company's code (`scoring/score_a.py` and `summarize_a.py` keep their
  structure, with empty tables or a generic subset).

Reviewers can ask the first author for access to the private material, under
the company's confidentiality terms.

## Pre-registration

Prompts and scoring rules were fixed before the first run, and the prompt
checksums were recorded in the environment report of each execution
(SHA-256):

| Prompt | Recorded checksum | This repository |
|---|---|---|
| `B0-assessment.md` | `ab295a23…ecda7d1` | identical |
| `B1-assessment.md` | `97b488fb…a878b6d` | identical |
| `P0-locate-and-snapshot.md` | `9b304e2c…ba23071` | identical (the organization is a placeholder, as in the template that was run) |
| `A-characterization.md` | `a9ebc8af…6192176` | differs only in line 5, where the list of service identifiers now uses the public names |

Run `shasum -a 256 prompts/*` to compare. The development history of this
material lives in a private repository; its commits, which date the prompts
and the scoring rules, can be shown to reviewers on request.

## Reusing the method on another system

1. Read `protocol/PROTOCOL.md` (design and controls) and
   `guides/execution-guide.md` (how the runs were executed).
2. Prepare the inputs: the questionnaire (`instruments/questionnaire.md`), a
   list of services, and a snapshot of their code without history
   (`tools/snapshot.sh`, or `prompts/P0-locate-and-snapshot.md` with an agent).
3. Run Task A with `prompts/A-characterization.md`, one chat per service, and
   check the cited locations with `tools/check_evidence.py`.
4. Run Tasks B0 and B1 with your own characterization, service descriptions
   and pattern catalog.
5. Score with the scripts in `scoring/` after filling in
   `scoring/questionnaires.py` and the reconciled characterization tables
   (format in `instruments/characterization-legend.md`).

The scripts expect the folder layout of the private repository
(`execution/results/A/<service>.json`, `execution-b/B0-inputs/characterization/`,
`execution-rerun/results/`); the guides use the same layout. Python 3.10 or
later, standard library only.

## Results in this repository

The article reports the reruns of Payin Processor, Agents Commissions and B1
(protocol Section 11, deviations 1 and 4). Files named `*-first-execution*`
hold the discarded first runs, used only to describe run-to-run variation.
Task B is scored against the revised answer key; `taskB-metrics-preregistered-key.csv`
holds the scores against the key registered before the runs (deviation 12).

## Use of AI

The study itself uses an LLM agent (Cursor, agent mode) for Tasks A and B.
An AI assistant also helped prepare the guides, the scripts and a first
assessment of the drawbacks (`checks/`), as stated in the article.

## Licence

Code (`tools/`, `scoring/`, `checks/*.py`) is released under the MIT License
(`LICENSE`). Text and data (everything else) are released under the Creative
Commons Attribution 4.0 International licence (`LICENSE-CC-BY-4.0.txt`).
Please cite the article when reusing this material.
