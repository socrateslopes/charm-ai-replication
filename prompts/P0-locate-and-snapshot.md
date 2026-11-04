<!-- Preparation step (not scored). Paste everything below the line into a NEW
     Cursor Agent chat opened on the folder ~/charm-kit. Fill in only ORG.
     This chat may use GitHub, the GitHub CLI (gh), git and the GitHub MCP
     server, but no other MCP server. -->
---

ORG: <GitHub organization that owns the repositories>

# Task: locate the code of five services and snapshot it at a cutoff date

You are preparing the inputs of a software architecture study. Find where
the code of each service listed in
`~/charm-kit/execution/A-inputs/services.csv` lives in the GitHub
organization `ORG`, and export a history-free snapshot of it as of the
cutoff date below. Do not analyze the architecture; only locate and copy.

- Cutoff: `2026-03-11 00:00 -0300`
- Snapshot tool: `~/charm-kit/execution/tools/snapshot.sh` (read its header
  for usage)
- Destination: `~/charm-study/A/repos/<service_id>/<repo-name>` (add
  `__<subdir-with-underscores>` to the folder name when you snapshot only a
  subfolder of a repository)

## Steps

1. For each service, search the organization (with `gh search repos`,
   `gh search code`, `gh repo list`, or GitHub MCP tools) for every
   repository, or subfolder of a monorepo, that contains:
   - the service's application code;
   - its module components deployed with it or for it (workers, schedulers,
     jobs, triggers, cron or workflow definitions), which usually share the
     service name as a prefix;
   - its deployment manifests (Kubernetes, Helm, Argo, CI/CD);
   - infrastructure-as-code that defines its queues, topics, buckets,
     caches or databases (only the files or folders specific to the
     service).

   Service names may appear with different spellings (hyphens, no spaces,
   camel case). Do not include code that belongs to other teams' services,
   even if it calls these services.
2. Write `~/charm-kit/execution/results/repo-map.csv` with the columns
   `service_id,repo,subdir,kind,default_branch,reason`, where `subdir` is `.`
   for a whole repository and `kind` is one of `code`, `component`,
   `deployment`, `iac`, `other`. Use one line per repository or subfolder.
3. Clone each repository into `/tmp/charm-clones/<repo>` and, for each line
   of `repo-map.csv`, run:
   ```bash
   bash ~/charm-kit/execution/tools/snapshot.sh /tmp/charm-clones/<repo> origin/<default_branch> <subdir> \
        "2026-03-11 00:00 -0300" ~/charm-study/A/repos/<service_id>/<folder> \
        ~/charm-kit/execution/results/snapshots.csv
   ```
4. Fill the `code_locations` column of
   `~/charm-kit/execution/A-inputs/services.csv` with the snapshot folders of
   each service, relative to `~/charm-study/A/` and separated by `;` (for
   example `repos/<service_id>/<folder>`).
5. Verify and print the results:
   ```bash
   find ~/charm-study/A/repos -name .git                 # must print nothing
   cat ~/charm-kit/execution/results/snapshots.csv      # every commit_date before 2026-03-11
   du -sh ~/charm-study/A/repos/*
   ```
6. Delete the clones: `rm -rf /tmp/charm-clones`.

## Rules

- Do not write anything inside `~/charm-study/` other than the snapshots,
  and do not change files in `~/charm-kit` other than the ones named above.
- Do not summarize, describe or analyze the code of the services, in files
  or in your replies.
- If a repository has no commit before the cutoff, record it in
  `repo-map.csv` with `kind=other` and the reason, and skip the snapshot.
- When you are unsure whether something belongs to a service, include it
  and say why in `reason`.
- Do not ask questions; record your decisions in `reason`.

When you finish, reply with the content of `repo-map.csv`, the output of
step 5, and the list of tools and MCP tools you used.
