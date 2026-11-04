# Experiment protocol: AI-assisted characterization and pattern-based assessment

Status: **pre-registered**. This file and the materials in `execution/`
(prompts, tools, templates, inputs) were committed before the first scored
run; the checksums of the prompts used are recorded in
`execution/results/environment.md`. Any later change is logged in Section 11
(Deviations). Step-by-step instructions are in `execution/README.md`.

Confidentiality: the repository is private. It contains the original
service names and the experiment outputs, which are renamed to the public
names before anything is published. It never contains source code or raw
interview transcripts. This file uses the public names.

---

## 1. Purpose

The original study (AsianPLoP 2026) characterized a five-service Payments
System with CharM using developer questionnaires, researcher cross-validation
(reconciliation), and expert interviews in which developers identified
existing patterns and suggested new ones from a pattern catalog. This
experiment replays the two knowledge-intensive steps of that process with an
LLM-based coding agent and compares the results with the validated outcomes
of the original study.

Research questions (to be integrated into the journal paper):

- **RQ2.** How accurately can an LLM agent characterize a service with
  CharM, given only static artifacts, compared with the developers'
  questionnaires and the reconciled characterization?
- **RQ3.** Can an LLM, given the characterization and a pattern catalog,
  identify the patterns already present and recommend refactoring patterns
  consistent with those identified by developers? How much does adding the
  developers' own input (questionnaire comments and interview excerpts)
  change the result?

## 2. Existing data from the original study (answer keys and inputs)

| Artifact | Content | Role here |
|---|---|---|
| Questionnaires (5; P1 to P5 each answered one service) | Developers' answers: responsibilities, endpoints and callers, outgoing calls, topics published and consumed, data sources, deployment dependencies, module components, overall comments. Never edited after submission, so they are the developers' first answers | Item-level answer key for A; responsibilities (Q2) and comments (Q10, Q11) are inputs to B |
| Reconciled characterization (spreadsheet tabs *Synchronous Calls*, *Asynchronous Calls*, *Databases*) | Pairwise counts of operations and topics between services, data-source access, after the researcher checked every questionnaire against code, API documentation and logs and clarified doubts with the participants | Pair-level answer key for A; input to B |
| Interview transcripts (7: P1 to P5 and the technical leaders P6 and P7; Portuguese) | Part 1 profile, Part 2 CharM evaluation and problems seen, Part 3 pattern identification and suggestion | Parts 1 and 2 are inputs to B1; Part 3 is never given to the agent |
| Pattern catalog (master's thesis, Appendix D; 23 patterns from chapters 4, 5 and 6 of Brown, Woolf and Yoder) | Problem, summary, typical implementation and benefits of each pattern, exactly as shown to participants | Input to B (`execution-b/B0-inputs/catalog.md`, generated from Appendix D) |
| Patterns identified (thesis figure "implemented patterns"; spreadsheet tab *reviewed of Patterns Identified*, column "Actual") | 14 patterns and the participants who recognized each | Answer key for B (patterns present) |
| Patterns suggested (thesis figure "patterns suggested"; spreadsheet tab *Copy of Patterns Suggestion*) | 9 patterns and the participants who suggested each | Answer key for B (recommendations) |
| Flaw categories (thesis Section "Architectural Problems Found in the Case Study"; AsianPLoP paper, Results) | Three categories of architectural flaws | Answer key for B (issues) |

### AI use in the original study (to be disclosed in the paper)

- Interviews were recorded in Google Meet and transcribed automatically by
  Gemini, which also generated meeting notes.
- In March 2026, Gemini Pro (Extended) was used to check the researcher's
  manual coding of the interviews for gaps (the "Tab 3" extractions). The
  coding itself was done manually.
- Developers were not asked whether they used AI assistants to answer the
  questionnaires. At least one answer shows signs of AI assistance. This was
  not part of the method, and every answer was cross-validated by the
  researcher and in the interviews.

## 3. Design

| Condition | Unit | Agent input | Runs | Answer keys |
|---|---|---|---|---|
| **A**: characterization | one service per chat (5 services) | code snapshot of the 5 services, blank questionnaire | 1 per service (5 chats) | questionnaires, reconciled characterization |
| **B0**: assessment, structural input only | whole system | system context, service responsibilities, reconciled characterization, pattern catalog | 1 | patterns identified, patterns suggested, flaw categories |
| **B1**: assessment with developer input | whole system | B0 inputs plus questionnaire comments and interview excerpts before the pattern stage | 1 | same as B0 |

- **A** mirrors the original *Divide and Conquer Service Characterization*:
  the same questionnaire, one service at a time.
- **B** uses the reconciled characterization, not the output of A, so that
  errors in A do not propagate into B and the two tasks are evaluated
  independently.
- **B0 vs B1** isolates the contribution of developers' tacit knowledge. In
  B1, rediscovering the flaws is expected (developers discussed them before
  the pattern stage), so flaw recall is evaluated primarily on B0.
- One run per service (A) and per condition (B0, B1), each in a fresh
  chat. Run-to-run variability is therefore not estimated; this is stated
  as a threat to validity.
- A preparation chat (P0, not scored) locates the repositories of each
  service by name and takes the code snapshot (Section 5).

## 4. Inputs given and withheld

Given to the agent: only what is listed in `execution/README.md` for each condition.

Never present on the execution machine during any run: the AsianPLoP paper,
the master's thesis, the full spreadsheet (only the three characterization
tabs are exported for B), answered questionnaires (for A), the Gemini
summaries ("Observações") and the "Tab 3" extractions of the transcripts,
the pattern stage of the interviews, any slides showing results, and the
rest of this repository (the execution computer uses a sparse checkout of
`execution/`; `execution-b/`, which contains the answer key of Task A, is
added only after Task A is finished).

The interview excerpts for B1 are produced by
`execution/tools/prepare_transcripts.py`, which keeps each transcript up to
the interviewer turn that opens the pattern stage (confirmed by the
researcher) and replaces names with participant IDs. The cut points are
recorded in `execution/results/transcript-cuts.csv`.

## 5. Code snapshot

- **Cutoff:** 2026-03-11 00:00 (UTC−03:00), the date of the first
  interview. The questionnaires were answered before the interviews, and
  pinning to the interview date avoids changes motivated by the interviews.
- The repositories are located by an agent (prompt P0) that searches the
  organization by service name for the code, module components, deployment
  manifests and infrastructure-as-code of each service. The researcher
  reviews the resulting map (`execution/results/repo-map.csv`).
- For each repository (or monorepo subdirectory) that contains code,
  configuration, deployment manifests or infrastructure-as-code of the five
  services and their module components, the last commit on the default
  branch before the cutoff is exported with `git archive`. The snapshot
  therefore contains **no git history**, so later commits cannot leak.
- Repository, path, commit SHA and commit date are recorded in
  `execution/results/snapshots.csv`. Other teams' services are not
  included.

## 6. Tooling and environment

- Agent: Cursor, Agent mode, on a computer that has never been used for
  this research conversation.
- Model: one model, selected explicitly (never "Auto") and kept identical
  for all chats. Recommended: the most capable Claude model available
  in Cursor. Record the exact model label, any context-size ("Max") or
  thinking setting, and the Cursor version.
- Disabled: User Rules, Project Rules added by the researcher, Memories,
  background agents, and every MCP server except GitHub's.
- Allowed: the agent's built-in tools (files, search, terminal), GitHub
  (GitHub MCP server, `gh`) and the internet (web search), as most
  developers would have them. The study's repositories are private, and
  web search cannot reach them; GitHub calls can, through the researcher's
  account, so auto-run is off and every terminal command and MCP call needs
  the researcher's approval. Calls that touch the study's repositories,
  GitHub searches not limited to the company's organization, and listings
  of the researcher's repositories are rejected. (The organization does not
  allow tokens restricted to it; if a separate account without access to
  the study's repositories is available, it is used instead.) The prompts
  forbid looking for the study,
  and in Task A, reading GitHub code newer than the cutoff or cloning
  repositories. Every MCP call, GitHub repository and web page the agent
  consults is recorded.
- Privacy Mode: on.
- Each chat starts empty (new chat) in a workspace that contains only the
  inputs of the current condition.

## 7. Execution procedure

1. Only the workspace of the condition being run exists on disk. Each
   output is moved out of the workspace to `execution/results/` as soon as
   its chat ends.
2. The prompt in `execution/prompts/` is pasted verbatim. Only the service
   ID (Task A) is filled in.
3. The researcher does not steer the agent. Only two standard messages are
   allowed, each at most twice per chat:
   - If the agent asks a question: *"Proceed with your best judgment,
     following the rules in the task, and record your assumptions."*
   - If the agent stops before writing all required outputs: *"Continue
     until all required outputs are written."*

   Any other interaction invalidates the run, which is then repeated and
   logged as a deviation. Approving or rejecting the agent's tool calls is
   not an interaction: local commands that read files, GitHub reads and web
   searches are approved; cloning, calls to MCP servers other than GitHub's,
   anything that looks for the study's materials, building or running code,
   and touching local files outside the workspace are rejected, and each
   rejection is logged in the run record.
4. The full chat is exported after each run.
5. If the agent reads local files outside the workspace, uses an MCP
   server other than GitHub's, or reads the study's materials (its
   repositories, the thesis or the paper), the run is invalid and is
   repeated. Reading GitHub code newer than the cutoff in Task A does not
   invalidate the run; it is recorded, and items supported only by such
   code are flagged in scoring.

## 8. Data recorded per run

Recorded in `execution/templates/run-record.md` (one per chat): task, date and start
and end time, machine OS, Cursor version, model label and settings, prompt
file checksum, MCP tools used, GitHub repositories and web pages consulted, snapshot SHAs (A) or input file checksums (B), number and
content of standard messages sent, usage or cost if shown, anomalies.

## 9. Scoring (specified before running)

Name matching between agent output and answer keys uses a normalization
(case, separators, environment prefixes such as `Prod`, path parameters)
plus an alias table built by the researcher. The alias table is published
with the results.

### 9.1 Task A

For each service and run, against the **questionnaire** (item level) and the
**reconciled characterization** (pair level):

- Q3 endpoints (Size): item-level precision, recall and F1; absolute error
  of the count (diagonal of *Synchronous Calls*).
- Q4 outgoing synchronous calls: precision, recall and F1 on
  (provider, endpoint); pair-level error of operation counts per provider.
- Q5/Q6 topics published and consumed: precision, recall and F1 on topics;
  pair-level error of topic counts per (publisher, subscriber).
- Q7 data sources: precision, recall and F1 on (data source, action).
- Q9 module components: precision and recall.
- Callers and consumers outside the five services cannot be observed in the
  snapshot. They are reported separately as *discoverability* (share of
  external callers and consumers the agent found or inferred) and are not
  counted as errors.
- **Reconciliation effect:** for every item where the questionnaire differs
  from the reconciled characterization, record whether the agent matches the
  reconciled value.
- **Evidence validity:** share of cited `path:line` that exist in the
  snapshot (automated, `execution/tools/check_evidence.py`), plus a manual
  check of a random sample of 20 items per service.
- **Error taxonomy (manual):** dynamic or unresolved configuration,
  possibly unused or dead code, naming mismatch, unsupported item (not in
  the code), out of scope.
- **Effort:** wall-clock time per service.

### 9.2 Tasks B0 and B1

- **Patterns present:** precision and recall against the 14 patterns
  identified by participants (Section 2). Patterns the agent
  reports beyond the answer key are checked by the researcher against the
  code and classified as supported or unsupported.
- **Recommended patterns:** recall of the 9 patterns suggested by
  participants (Section 2), both overall and restricted to patterns suggested
  by two or more participants.
- **Issues:** recall of the three flaw categories of the original study.
  An issue matches a category when it names at least one of the same
  services and the same mechanism (excessive synchronous coupling or single
  point of failure on a third party; hub service with high afferent
  coupling; oversized services with blurred domain boundaries).
- **Groundedness:** share of evidence references that exist in the inputs
  (automated), and share that support the claim (researcher, all
  recommendations).
- **Catalog conformance:** share of recommendations that use an exact
  catalog name.
- **Drawbacks:** each stated drawback is classified as *documented* (listed
  in the consequences of the pattern in Brown, Woolf and Yoder, *Cloud
  Application Architecture Patterns*), *plausible but undocumented*, or
  *not applicable*.
- **New suggestions** (not in the answer key): reported descriptively and
  classified by the researcher as consistent or inconsistent with the
  evidence. Single-rater coding is a stated threat to validity.
- **B0 vs B1:** differences in all of the above.

## 10. Threats addressed by design

| Threat | Mitigation |
|---|---|
| Agent sees results of the original study | Separate computer; answer keys not on the machine; study repositories private; every GitHub call approved by hand and limited to the company's organization; prompts forbid searching for the study; GitHub and web use logged and audited; paper unpublished |
| Code evolved after March | Snapshot at the interview date without history; GitHub reads restricted to commits before the cutoff and audited |
| Leakage between conditions or runs | Sparse checkout; one condition on disk at a time; outputs moved out of the workspace after each chat |
| Researcher steering | Fixed prompts; only two standard messages; pre-registered scoring |
| Answers in the transcripts | Pattern stage excluded; flaw recall measured on B0 |
| Run-to-run variation | Not controlled (one run per condition); stated as a threat to validity |
| Unequal instrument | Agent answers the same questionnaire as developers; B gets the same catalog |
| Developer baseline partly AI-assisted | Reconciled, researcher-verified characterization is the primary answer key; stated as a limitation |

## 11. Deviations

Found while scoring (2026-10-01). Decisions marked *open* are the
researcher's to take.

| # | Deviation | Effect | Runs | Decision |
|---|---|---|---|---|
| 1 | The agent read Cursor's own transcript of the current chat, a file outside the workspace, once each, to recover context after a summary. It contained only the task prompt. Both agents disclosed it in their logs. | No study data read. Breaks rule 1 of prompt A; Section 7.5 says such runs are repeated. | A: payin-processor, agents-commissions | Repeat (decided 2026-10-01): `execution-rerun/`, same inputs and prompt, auto-run set to ask so such reads can be rejected; at most one more repetition |
| 2 | agents-commissions: a `gh` command wrote `/tmp/null` by mistake; the agent deleted it and logged it. | None. | A: agents-commissions | keep, disclose |
| 3 | `sync.csv` given to B0 and B1 has an empty `bank-interface` diagonal (Size 14 in the public tab). Export error. | Both agents noticed and treated bank-interface' Size as unknown. | B0, B1 | *open*: disclose (recommended) or fix and repeat |
| 4 | The P5 excerpt ends after the interviewer opens the pattern stage and lists four catalog patterns, saying that each service in the system uses its own language. P4 ends with the interviewer's opening sentence of the pattern stage, which names no pattern. The script suggested a later cut and it was accepted. | B1 did not cite P5 after 00:30:26; its Polyglot Development claim cites the questionnaires and P7 (before the pattern stage). Breaks Section 4. | B1 | Repeat (decided 2026-10-01) with P4 and P5 cut before the opener (`execution-rerun-b/`, `execution-rerun/results/transcript-cuts-B1.csv`); other inputs unchanged, including the bank-interface cell of deviation 3, to keep B0 and B1 comparable |
| 5 | Run records were not filled in; `environment.md` lacks the auto-run setting, enabled MCP servers, the GitHub account used and the per-chat tool list. | Tool use was reconstructed from the agents' logs and chat exports: no MCP server and no web page were used in any chat; GitHub was used through `gh` only, scoped to the organization. | all | Completed in `environment.md`: only GitHub's MCP server was enabled and it was not used; the GitHub account was not recorded |
| 6 | The answered P0 prompt with the organization filled in was committed. | Company name in the repository (private). | P0 | Resolved (2026-11-04): the public replication package contains the P0 template as it was run, with the organization as a placeholder (its checksum matches the recorded one); the private repository keeps the answered prompt |
| 7 | The manual check of 20 cited locations per service (Section 9.1) was not done: the snapshot was deleted after Task A (README Part 5). | Content of citations not yet checked; existence was checked automatically. | A | Done 2026-10-02 after rebuilding the snapshot (`experiment/checks/check_citations.py`, results in `experiment/checks/results/check1-citations.csv`): 20 items per service from the final runs, fixed seed; the first cited location supported the item in 93 of 100, partly in 5, not in 2. Only the first location of each item was shown, so an item with other supporting citations can be rated *no*; 6 of the 7 non-*yes* items also cite other locations, which were not checked |
| 8 | Drawbacks "documented in Brown, Woolf and Yoder" (Section 9.2) cannot be checked from the catalog, which has no drawbacks. | Checked against the full text of chapters 4–6 (2026-10-02): B0 7 of 22 stated, 8 partly; B1 13 of 37 stated, 13 partly (`experiment/checks/check2-drawbacks.csv`), after the spot-check below. The planned scale (documented / plausible but undocumented / not applicable) was replaced by yes / partly / no, where *partly* is a related or more general concern (including the chapter-level disadvantages of the architecture) and *no* is mostly system-specific; plausibility was not rated. | B0, B1 | At the researcher's request, the check was done by Claude (the assistant used for scoring), not by the researcher; the researcher spot-checked 15 verdicts (5 per verdict, fixed seed; `experiment/checks/results/check2-spotcheck.csv`) on 2026-10-03, agreed with 14 and changed B1-R1-D6 from partly to no. Disclosed in the paper |
| 10 | No terminal command or tool call asked for approval (auto-run was not set to ask), so the safeguard of Section 6 (each GitHub call approved by hand) did not operate in the first execution. | The audit of the agents' logs and chat exports found GitHub access only to the company's organization, through `gh`, and no access to the study's repositories or to the web. | all first-execution runs | Disclose; the reruns use auto-run set to ask |
| 11 | Rerun executed 2026-10-01 (`execution-rerun/`). Snapshot rebuilt at the recorded commits (145 folders); prompts unchanged; only P4 and P5 differ in the B1 inputs. No chat read files outside its workspace, used an MCP server, or used the web. The rerun report and run records were left blank, so the auto-run setting of the rerun is not recorded. | The reruns replace the first-execution runs of payin-processor, agents-commissions and B1 in the results; the first-execution runs are kept and scored separately (`experiment/scoring/results/first-execution/`) to describe run-to-run variation. Issues of the B1 rerun were matched to the flaw categories again (`score_b.py`). | A: payin-processor, agents-commissions; B1 | The researcher reports that no approval was requested in the rerun either; whether auto-run was set to ask is not recorded. Disclosed; the audit of logs and chats is the control that was applied |
| 9 | Patterns reported beyond the answer key (Event Backbone, Domain Event, Service Orchestrator in B0 and B1; Application Services and Bounded Context in B1) needed the researcher's check against the code. | Checked by the researcher 2026-10-03 (`experiment/checks/check3-extra-patterns.md`): Service Orchestrator supported; Event Backbone partly (Kafka shared and run by another team, SNS/SQS managed by each team); Domain Event partly (informal practice, judged the same as the participants' Event); Application Services unsupported (the APIs orchestrate rather than delegate to a domain layer; revised by the researcher the same day) and Bounded Context unsupported. Precision counting supported patterns: B0 8/10 (10/10 with partly), B1 10/14 (12/14). | B0, B1 | Done; the answer-key precision stays the primary metric |
| 12 | After the runs and the checks (2026-10-30), the dissertation's re-check of the transcripts revised the participants' pattern counts: Repositories identified by 2 participants (was 1), Event Backbone identified and suggested by P1 (new), Event Notifier suggested by 3 (the spreadsheet tab used for scoring said 2). The revision was made for the dissertation, but after both agents and check 3 had named Event Backbone. | Answer key: 15 patterns present (42 mentions), 10 suggested (28). Precision B0 7/10 → 8/10, B1 9/14 → 10/14; recall 7/14 → 8/15 and 9/14 → 10/15; suggested patterns recommended 4/9 → 4/10. Conclusions unchanged. | B0, B1 | Researcher's decision (2026-11-04): score against the revised key for consistency with the dissertation; the pre-registered key is kept (`score_b.py --preregistered-key`) and its results are reported in the paper |
