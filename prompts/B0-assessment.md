<!-- Paste everything below the line into a NEW Cursor Agent chat opened on
     ~/charm-study/B0. There is nothing to fill in. -->
---

# Task: pattern-based assessment of a service-based architecture

You are assisting a software architecture research study. Using only the
material in `inputs/`, assess the architecture of the system described there
against a pattern catalog, and recommend improvements.

## Inputs

- `inputs/system-context.md`: the system, its domain and its scope.
- `inputs/services.md`: the responsibilities of each in-scope service, as
  described by its developers.
- `inputs/characterization/`: a characterization of the system along four
  dimensions (Size, Data Source Coupling, Synchronous Coupling, Asynchronous
  Coupling). Read `legend.md` first; it explains the three tables
  `sync.csv`, `async.csv` and `databases.csv`.
- `inputs/catalog.md`: the pattern catalog. Each pattern has a name, a
  description, typical implementations and benefits.

## Rules

1. Base your assessment of the system on the files in `inputs/`. Do not
   read local files outside this workspace, including through terminal
   commands.
2. You may use GitHub (the GitHub MCP server, `gh`) and the internet (web
   search, web pages) for general knowledge, such as patterns, frameworks or
   technologies, with these limits:
   - Do not look for the code, documentation or repositories of the system
     described in the inputs, or for publications, theses, slides or
     repositories that describe this study or its results.
   - On GitHub, read only public repositories that you name explicitly. Do
     not run searches across GitHub and do not list the repositories of
     your user account.
   - Do not use any MCP server other than GitHub's.
   - Record every GitHub repository and web page you consult in your log.
3. Cite evidence for every claim, using only references that exist in the
   inputs:
   - `SYNC[sender->receiver]`: a cell of `sync.csv` (use the same name on
     both sides for the diagonal, e.g. `SYNC[x->x]`);
   - `ASYNC[publisher->subscriber]`: a cell of `async.csv`;
   - `DB[data source]`: a row of `databases.csv`;
   - `SVC[service]`: a service description in `services.md`;
   - `CTX`: `system-context.md`.
4. Recommendations must use pattern names exactly as written in the
   catalog. Put anything that is not a catalog pattern in
   `other_suggestions`.
5. The catalog does not describe drawbacks. Reason about them yourself, for
   this specific system.
6. If the evidence is insufficient to support a claim, say so instead of
   making it.
7. Do not ask questions. When something is ambiguous, decide, and record it
   under `assumptions`.
8. Write in English.

## Steps

1. **Patterns present.** Identify which catalog patterns the system
   currently implements, fully or partially, and in which services.
2. **Issues.** Identify architectural problems in the system. Relate each
   one to the dimensions in which it shows up.
3. **Recommendations.** For each issue, recommend zero or more catalog
   patterns. For each recommendation, explain why it fits, which benefits
   you expect, and which drawbacks and risks applying it in this system
   would bring. List the alternatives you considered and why you did not
   choose them.
4. **Prioritization.** Rank the recommendations. State the criteria you
   used and how each recommendation meets them.

## Output

Write `outputs/assessment.json` with exactly this structure:

```json
{
  "patterns_present": [
    {"pattern": "", "status": "implemented | partial", "services": [""], "rationale": "", "evidence": [""]}
  ],
  "issues": [
    {"id": "I1", "title": "", "description": "", "services": [""], "dimensions": [""], "evidence": [""]}
  ],
  "recommendations": [
    {"id": "R1", "addresses": ["I1"], "pattern": "", "services": [""], "rationale": "",
     "expected_benefits": [""], "drawbacks": [""],
     "alternatives_considered": [{"option": "", "why_not": ""}],
     "priority": 1, "priority_rationale": "", "evidence": [""]}
  ],
  "prioritization_criteria": [""],
  "other_suggestions": [
    {"suggestion": "", "addresses": ["I1"], "rationale": "", "evidence": [""]}
  ],
  "assumptions": [""],
  "limitations": ""
}
```

Also write `outputs/log.md` with the start and end time (taken with `date`),
the order in which you read the inputs, the tools you used, including every
MCP tool, and every GitHub repository and web page you consulted, and why.

When you finish, reply with a short summary of your top three
recommendations.
