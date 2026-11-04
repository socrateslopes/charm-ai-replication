# Supplement

Details referred to in the article as "Supplement S1" to "S4". Service names
are the fictitious ones used in the article. Counts come from the files in
`results/` and `checks/`.

## S1. Controls of the agent runs

The full design is in `protocol/PROTOCOL.md` (Sections 4 to 8) and the
execution steps in `guides/`. In summary:

- **Inputs.** Task A received a history-free snapshot of the code,
  configuration and deployment files of the five services at the last commit
  before the first interview (11 March 2026), the questionnaire, and the list
  of services. Tasks B0 and B1 received the reconciled characterization, the
  service descriptions written by the developers, the system context and the
  catalog as shown to participants; B1 also received the developers'
  questionnaire comments and the interview excerpts up to the point where the
  catalog was introduced (`instruments/`).
- **Isolation.** The runs used a computer never used for this research. The study repository was downloaded with a sparse checkout, so
  that the answer keys and the paper were never on that computer, and each
  chat started in a workspace that held only the inputs of its condition.
- **Agent configuration.** Cursor 3.22.12 in agent mode, one model selected
  explicitly and kept constant, Privacy Mode on, no memories or custom rules,
  every MCP server except GitHub's disabled.
- **Tool policy.** The agent could read GitHub and search the web. The prompts
  limited GitHub to the company's organization, forbade searching for the
  study, and, in Task A, forbade reading code newer than the cutoff. The
  agent logged every repository and web page it consulted; the audit of the
  logs and chat exports found GitHub access only to the organization and no
  use of the web.
- **Researcher input.** Prompts were pasted verbatim. The researcher could
  send two standard messages only: "Proceed with your best judgment,
  following the rules in the task, and record your assumptions." and
  "Continue until all required outputs are written."
- **Repeated runs.** Three runs broke a rule and were repeated with the same
  prompts and inputs (`guides/rerun-guide.md`): in Task A for Payin
  Processor and Agents Commissions, the agent read its own chat transcript,
  a file outside its workspace, to recover context after a summary
  (protocol Section 11, deviation 1); the interview excerpts of the first B1
  run included the opening of the pattern stage for one participant
  (deviation 4). The article reports the repeated runs.
- **Approvals.** No terminal command or tool call asked for approval in
  either execution, so the manual approval of GitHub calls planned in the
  protocol did not operate; the audit above is the control that was applied
  (deviations 10 and 11).

## S2. Task A: further results

**Item level against the developers' questionnaires (micro-averaged over the
five services).** Per service: `results/taskA-items.csv`.

| Question | Questionnaire | Agent | Matched | Precision | Recall | F1 |
|---|---|---|---|---|---|---|
| Q3 operations exposed | 118 | 149 | 117 | 0.79 | 0.99 | 0.88 |
| Q4 outgoing synchronous calls | 56 | 79 | 55 | 0.70 | 0.98 | 0.81 |
| Q5 topics published | 54 | 71 | 51 | 0.72 | 0.94 | 0.82 |
| Q6 topics consumed | 55 | 64 | 50 | 0.78 | 0.91 | 0.84 |
| Q7 data sources | 12 | 21 | 11 | 0.52 | 0.92 | 0.67 |
| Q9 module components | 13 | 35 | 12 | 0.34 | 0.92 | 0.50 |

**Items that differ from the questionnaires** (`results/taskA-differences-by-category.csv`).
Of the 123 items the agent reported and the developers did not:

| Category | Items |
|---|---|
| Flagged by the agent, or marked in the code, as possibly unused, legacy or test-only | 35 |
| Platform concerns the questionnaire does not ask about (health and metrics endpoints, authorization, change-data-capture topics, monitoring jobs) | 31 |
| Different granularity or module boundary (e.g., a scheduler reported as a module component rather than as an external publisher) | 20 |
| Naming or HTTP-method mismatch | 5 |
| Recorded neither by the developers nor by the reconciliation | 32 |

The agent missed 12 items: 9 not explained by these categories, 2 naming
mismatches and 1 granularity difference.

**Relation level against the reconciled characterization**
(`results/taskA-relations.csv`).

| Relation | Recorded | Agent recall | Agent precision | Developers' recall | Developers' precision |
|---|---|---|---|---|---|
| Services invoked | 12 | 1.00 | 0.48 | 0.92 | 1.00 |
| Invoking services | 28 | 0.75 | 0.64 | 1.00 | 1.00 |
| Subscribers | 12 | 0.83 | 0.45 | 1.00 | 1.00 |
| Publishers | 8 | 0.88 | 0.70 | 1.00 | 1.00 |
| Data sources | 12 | 0.92 | 0.52 | 1.00 | 1.00 |
| All | 72 | 0.85 | 0.55 | 0.99 | 1.00 |

The developers' only missing relation is the webhook from Credit Card
Processor to Payin Processor, which the reconciliation added and the agent
found. The agent also matched the other reconciliation correction: Payin
Processor invokes 24 distinct operations of its bank provider (20 in the
questionnaire).

**Evidence** (`results/taskA-evidence.csv`, `results/check1-citations-summary.csv`).
The agent cited 1,321 locations: 1,192 in the snapshot, of which 1,189
exist and are within range, and 129 in other repositories of the
organization at a named commit (77 at a snapshot commit, 52 at another
commit). In the manual check of 20 items per service (fixed random sample;
`checks/check_citations.py`), the first cited location supported the item
in 93 cases, partly in 5 and not in 2; 6 of the 7 items that were not fully
supported also cite other locations, which were not checked.

**Run-to-run variation** (`results/taskA-items-first-execution.csv`). The
repeated run of Payin Processor found the same 41 operations and the same
relations as the first run, but flagged 9 operations as possibly unused
instead of 1. For Agents Commissions, the first run found all 8 invoking
services, partly from access-control grants in another team's repository;
the repeated run did not consult that repository and found 3.

## S3. Task B: further results

**Patterns reported as present.** "Key" marks patterns in the answer key;
the verdicts of the others come from the researcher's check against the code
(`checks/check3-extra-patterns.md`).

| Pattern | B0 | B1 | Status |
|---|---|---|---|
| Domain Microservice, Self-Managed Data Store, Adapter Microservice, Anti-Corruption Layer, Event Notifier, Reactive Component, Event Choreography | yes | yes | Key |
| Event Backbone | yes | yes | Key (one participant); in the code, partly: Kafka is a shared platform run by another team, while each team creates its own SNS topics and SQS queues |
| Polyglot Development, Repositories | – | yes | Key |
| Service Orchestrator | yes | yes | Supported: Payout Processor and Bank Interface drive each payment through the bank and record it in the ledger and the ERP |
| Domain Event | yes | yes | Partly: events exist, as a practice rather than a design decision (past-tense and command-like names are mixed); judged the same as the Event pattern participants named |
| Application Services | – | yes | Unsupported: the APIs orchestrate payments rather than delegate to a domain layer |
| Bounded Context | – | yes | Unsupported: services keep their models apart, but no context boundaries were defined |

**Recommendations, in priority order.**

| Priority | B0 | B1 |
|---|---|---|
| 1 | Event Choreography (Payin Processor, Credit Card Processor) | Reactive Component (Bank Interface monthly batch) |
| 2 | Anti-Corruption Layer (Payin Processor's bank integration) | Adapter Microservice (Payin Processor's bank integration) |
| 3 | Context Map (all services) | Context Map (all services) |
| 4 | Event API (all services) | Event API (all services) |
| 5 | Domain Microservice (Pay Out services) | Event Choreography (Payin Processor) |
| 6 | Dispatcher (Agents Commissions, Payout Processor) | Domain Microservice (Pay Out services) |
| 7 | Self-Managed Data Store (Payin Processor, Bank Interface) | Domain Microservice (Payin Processor) |
| 8 | – | Dispatcher (Agents Commissions) |
| 9 | – | Self-Managed Data Store (Payin Processor, Bank Interface) |

Every recommendation lists drawbacks (22 in B0, 37 in B1) and one to four
rejected alternatives (16 in B0, 23 in B1). Both conditions also listed
suggestions outside the catalog, among them timeouts and circuit breakers on
the synchronous calls to external providers.

**Further metrics** (`results/taskB-metrics*.csv`).

| Metric | B0 | B1 | B1, first run (discarded) |
|---|---|---|---|
| Patterns present: precision | 8/10 | 10/14 | 10/13 |
| Patterns present: recall | 8/15 | 10/15 | 10/15 |
| Patterns present: recall weighted by participants | 27/42 | 32/42 | 32/42 |
| Suggested patterns recommended | 4/10 | 4/10 | 7/10 |
| ... suggested by at least two participants | 4/8 | 4/8 | 7/8 |
| Distinct recommended patterns that participants suggested | 4/7 | 4/8 | – |

**Drawbacks against the source book** (`checks/check2-drawbacks.csv`). Each
of the 59 drawbacks was classified as stated in the book in substance, partly
stated (a related or more general concern), or not stated: B0 7, 8 and 7; B1
13, 13 and 11. Most of the drawbacks not stated concern the system rather
than the pattern (migration risks, teams that would have to agree, a service
becoming more central). An LLM assistant made the first classification from
the book's text; the first author checked a stratified random sample of 15
verdicts and agreed with 14 (`checks/check2-spotcheck.csv`).

## S4. Answer key

The answer key for Task B is the set of patterns and concepts the participants
recognized as present (13 patterns and two related concepts, Repositories and
Ubiquitous Language, the second not a catalog entry; 42 mentions), the patterns they suggested as refactoring targets (10
patterns, 28 mentions), and the three categories of problems. A re-check of
the interview transcripts after the runs added Event Backbone (one
participant) to both sets, a second mention of Repositories, and a third
suggestion of Event Notifier (protocol Section 11, deviation 12). The article
reports the results against this revised key.

Against the key registered before the runs (14 recognized, 40 mentions; 9
suggested, 26 mentions; `results/taskB-metrics-preregistered-key.csv`):
precision 7/10 (B0) and 9/14 (B1), recall 7/14 and 9/14, and suggested
patterns recommended 4/9 and 4/9.
