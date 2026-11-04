<!-- Paste everything below the line into a NEW Cursor Agent chat opened on
     ~/charm-study/A. Fill in only SERVICE_ID. Do not change anything else. -->
---

SERVICE_ID: <payin-processor | credit-card-processor | agents-commissions | bank-interface | payout-processor>

# Task: characterize one service from its source code

You are assisting a software architecture research study. Your job is to
characterize the service `SERVICE_ID` by answering the questionnaire in
`inputs/questionnaire.md`, using only the files in this workspace. The
developers who maintain the service answered the same questionnaire. Answer as
completely and accurately as the files allow.

## Workspace

- `repos/`: read-only snapshots of the code, configuration and deployment
  files of the services in scope. There is no git history.
- `inputs/services.csv`: the services in scope and where their files are in
  `repos/`.
- `inputs/snapshots.csv`: for each snapshot folder, the GitHub repository it
  came from and the commit it was taken at (the last commit before the
  cutoff, 2026-03-11 00:00 -0300).
- `inputs/questionnaire.md`: the questionnaire.
- `outputs/`: where you write your results.

## Rules

1. The snapshots in `repos/` are your primary source. Do not read local
   files outside this workspace, including through terminal commands.
2. You may use GitHub (the GitHub MCP server, `gh`) and the internet (web
   search, web pages), with these limits:
   - On GitHub, read only repositories of the organization that owns the
     repositories in `inputs/snapshots.csv`, and public repositories. Read
     them at a commit on or before the cutoff (for the snapshot
     repositories, the commit in `inputs/snapshots.csv`). Read through the
     API or web pages; do not clone repositories. Limit every GitHub
     search to that organization (`org:<owner>` or `repo:<owner>/<repo>`),
     and do not list the repositories of your user account.
   - Do not look for publications, theses, slides or repositories that
     describe this study or its results.
   - Do not use any MCP server other than GitHub's.
   - Do not connect to databases, message brokers, cloud consoles or running
     systems. Do not install packages, build, run or test the code.
   - Record every GitHub repository and web page you consult in your log.
3. Do not create or modify files anywhere except `outputs/`.
4. You may read the files of the other services in `repos/` to find out who
   calls or consumes what, but answer the questionnaire for `SERVICE_ID`
   only, including its module components (workers, schedulers and similar
   units deployed with it).
5. Every item you report must cite evidence as one or more locations in the
   form `repos/<path>:<line>` or `repos/<path>:<start>-<end>`. Evidence found
   only on GitHub outside the snapshot is cited as
   `github:<owner>/<repo>@<commit-sha>:<path>:<line>`, and evidence found
   only on the web as `web:<url>`. Prefer the snapshot when the same file is
   in `repos/`. Do not copy
   source code, secrets, credentials, internal hostnames or personal data
   into your answers.
6. Classify the evidence of each item with `evidence_type`: `code`,
   `config` (configuration, deployment or infrastructure files),
   `documentation`, or `inferred` (deduced from naming or indirect clues
   without a direct declaration).
7. If a value cannot be fully determined from the files (for example, a
   queue name or URL that comes from an environment variable defined
   outside the workspace), report the item anyway with `"resolved": false`
   and explain in `notes`. Do not guess silently and do not leave items out.
8. Callers and consumers outside `repos/` are not in the snapshot. You may
   look for them in the organization's repositories on GitHub (rule 2), or
   report those you can support with documentation or configuration, marked
   `inferred` when there is no direct declaration.
9. Report what exists in the snapshot. If something looks unused or
   deprecated, still report it, set `"possibly_unused": true`, and explain in
   `notes`.
10. Name in-scope services with the `service_id` from `inputs/services.csv`.
    Name everything else (external services, providers, topics, queues, data
    sources) as declared in the files, after resolving any variables you can
    resolve.
11. Do not ask questions. When something is ambiguous, decide, apply the
    decision consistently, and record it under `assumptions`.
12. Keep working until all outputs are written.

## Output

Write `outputs/SERVICE_ID.json` with exactly this structure. Arrays may be
empty, and every `evidence` array must be non-empty.

```json
{
  "service_id": "",
  "q2_responsibilities": "",
  "q3_endpoints": [
    {"endpoint": "METHOD /path", "consumed_by": [{"service": "", "evidence_type": "", "evidence": [""]}],
     "possibly_unused": false, "evidence_type": "", "evidence": [""], "notes": ""}
  ],
  "q4_sync_calls": [
    {"endpoint": "METHOD /path-or-url-template", "provider": "", "resolved": true,
     "evidence_type": "", "evidence": [""], "notes": ""}
  ],
  "q5_topics_published": [
    {"topic": "", "consumed_by": [{"service": "", "evidence_type": "", "evidence": [""]}],
     "resolved": true, "possibly_unused": false, "evidence_type": "", "evidence": [""], "notes": ""}
  ],
  "q6_topics_consumed": [
    {"topic": "", "produced_by": [{"service": "", "evidence_type": "", "evidence": [""]}],
     "resolved": true, "possibly_unused": false, "evidence_type": "", "evidence": [""], "notes": ""}
  ],
  "q7_data_sources": [
    {"name": "", "type": "", "role": "", "actions": "read | write | read/write",
     "shared_by": [{"service": "", "evidence_type": "", "evidence": [""]}],
     "resolved": true, "evidence_type": "", "evidence": [""], "notes": ""}
  ],
  "q8_deployment_dependencies": [
    {"service": "", "why": "", "evidence_type": "", "evidence": [""]}
  ],
  "q9_module_components": [
    {"service": "", "what_it_does": "", "evidence_type": "", "evidence": [""]}
  ],
  "q10_overall_assessment": "",
  "q11_other_comments": "",
  "assumptions": [""],
  "limitations": ""
}
```

Also write `outputs/SERVICE_ID.log.md` containing:

- the start and end time, taken with `date` at the beginning and at the end
  of your work;
- a short list of the steps you took (what you searched for and where);
- the tools you used, including every MCP tool;
- every GitHub repository (with the commit you read) and web page you
  consulted, and why;
- anything that limited your analysis (missing configuration, generated
  code, dynamic routing, and so on).

When you finish, reply with the number of items in each section (Q3 to Q9)
and one paragraph on what you could not determine and why.
