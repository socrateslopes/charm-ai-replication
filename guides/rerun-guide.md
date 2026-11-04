# Rerun: Task A (payin-processor, agents-commissions) and Task B1

This folder repeats three runs of the first execution. Nothing in
`execution/` or `execution-b/` changes, and the first run's results stay where
they are. The new results go to `execution-rerun/results/`.

| Run | Why it is repeated (protocol Section 11) | What changes |
|---|---|---|
| A, `payin-processor` | The agent read a file outside the workspace (its own chat transcript) | Nothing in the inputs. Auto-run is now set to ask, so you can reject such reads |
| A, `agents-commissions` | Same | Same |
| B1 | The P5 excerpt included the start of the pattern stage (P4 its first sentence) | `execution-rerun-b/B1-inputs/`: P4 and P5 now end before the interviewer opens the pattern stage. All other inputs are identical |

The prompts are the same files as in the first run (`execution/prompts/`), so
their checksums must match the ones in `execution/results/environment.md`.
Use **the same model, Max mode and thinking settings** as the first run
(recorded in `execution/results/environment.md`).

**Layout**

| Folder | Content | On the execution computer |
|---|---|---|
| `execution/prompts/`, `execution/A-inputs/`, `execution/templates/`, `execution/tools/`, `execution/results/snapshots.csv` | Same prompts, inputs, templates and tools as the first run | From Part 1 |
| `execution-rerun/` | This guide, the snapshot rebuild tool, the rerun results | From Part 1 |
| `execution-b/B0-inputs/`, `execution-rerun-b/` | B1 inputs (they include the answer key of Task A) | **Only from Part 5** |
| Everything else, including `execution/results/` of the first run | Answer keys and first-run outputs | **Never** |

**Time:** about 2 hours (rebuild 20–40 min, each chat 15–25 min).

**The two standard messages** are the same as before (M1 if the agent asks a
question, M2 if it stops early; each at most twice per chat):

- **M1:** `Proceed with your best judgment, following the rules in the task, and record your assumptions.`
- **M2:** `Continue until all required outputs are written.`

---

## Part 1. Prepare the execution computer (~15 min)

Use the same computer as before, or another one never used for this research.

1. Download only what the rerun needs. This is a new folder; do not reuse
   `~/charm-kit`, which has the first run's results and the B inputs.
   ```bash
   git clone --filter=blob:none --no-checkout <URL of this repository> ~/charm-kit-rerun
   cd ~/charm-kit-rerun
   git sparse-checkout set --no-cone /execution/prompts/ /execution/A-inputs/ /execution/templates/ \
       /execution/tools/ /execution/results/snapshots.csv /execution-rerun/
   git checkout main
   ls ~/charm-kit-rerun ~/charm-kit-rerun/execution ~/charm-kit-rerun/execution/results
   ```
   The last command must show only `execution` and `execution-rerun` at the
   top, and only `snapshots.csv` in `execution/results`.
2. Move the first run's folders out of the way so that the agent cannot find
   them on disk. If you already deleted `~/charm-kit` and `~/charm-study`, the
   first two commands do nothing; still do the Cursor step below, because
   Cursor keeps its own copy of the old chats.
   ```bash
   mkdir -p ~/charm-archive
   [ -d ~/charm-kit ] && mv ~/charm-kit ~/charm-archive/
   [ -d ~/charm-study ] && mv ~/charm-study ~/charm-archive/
   ```
   (Or delete them: everything from the first run is already in the
   repository.) Then **quit Cursor** and move its stored history of the
   first-run chats, which includes their transcripts:
   ```bash
   ls -d ~/.cursor/projects/*charm* 2>/dev/null
   for d in ~/.cursor/projects/*charm*; do [ -d "$d" ] && mv "$d" ~/charm-archive/; done
   ```
   Open Cursor again afterwards.
3. Check that the prompts are the same as in the first run:
   ```bash
   cd ~/charm-kit-rerun && shasum -a 256 execution/prompts/A-characterization.md execution/prompts/B1-assessment.md
   ```
   Expected:
   ```
   a9ebc8afac9ee9429b163e50b2d22f29577c21bf806491d82b84618646192176  execution/prompts/A-characterization.md
   97b488fbc10d3c9ad1e850f526832fe875dcb7a24cc9cd3e572b8a7fea878b6d  execution/prompts/B1-assessment.md
   ```
   If they differ, stop and report it.
4. Start the report:
   ```bash
   cp execution-rerun/templates/environment.md execution-rerun/results/environment.md
   ```
5. In **Cursor Settings** (names vary between versions):
   - Same as the first run: Privacy Mode on; no User Rules; Memories off;
     background agents off; web search on; same model, Max mode and thinking
     settings.
   - **MCP:** only GitHub's server enabled (as before).
   - **Auto-run: "Ask every time"** (or "Use allowlist" with an empty
     allowlist). This is the one change from the first run: every terminal
     command and tool call must wait for your approval. If your version has
     an **"External-file protection"** or similar option, turn it on.
   - Start a **new chat** for every run, never continue an old one.
6. Fill in the top of `execution-rerun/results/environment.md`.

## Part 2. Rebuild the snapshot of Task A (~20–40 min)

The agent must see exactly the same files as in the first run. The tool
re-exports every folder listed in `execution/results/snapshots.csv` at the
same commit, without git history. It uses your own GitHub access (the same
way P0 did); no agent is involved.

1. In Terminal:
   ```bash
   mkdir -p ~/charm-rerun/A/inputs ~/charm-rerun/A/outputs
   python3 ~/charm-kit-rerun/execution-rerun/tools/rebuild_snapshot.py \
       ~/charm-kit-rerun/execution/results/snapshots.csv ~/charm-rerun/A \
       ~/charm-kit-rerun/execution-rerun/results/A/rebuild-manifest.csv
   ```
   It must end with `OK` (145 folders rebuilt, no `.git` folders).
2. Copy the inputs, which are the same files as in the first run:
   ```bash
   cp ~/charm-kit-rerun/execution/A-inputs/questionnaire.md ~/charm-kit-rerun/execution/A-inputs/services.csv \
      ~/charm-kit-rerun/execution/results/snapshots.csv ~/charm-rerun/A/inputs/
   rm -rf /tmp/charm-rerun-clones
   ```
3. In Cursor: *File → Open Folder…* → `~/charm-rerun/A`. Wait until indexing
   finishes.

## Part 3. Run Task A: `payin-processor`, then `agents-commissions` (2 chats)

**For each service:**

1. Create the run record and write the start time in it:
   ```bash
   cp ~/charm-kit-rerun/execution/templates/run-record.md ~/charm-kit-rerun/execution-rerun/results/A/run-record_<service>.md
   ```
2. New chat (`+`), **Agent** mode, the same model.
3. Open `~/charm-kit-rerun/execution/prompts/A-characterization.md`, copy
   everything below the `---` line, paste it into the chat, and change only
   the first line, e.g. `SERVICE_ID: payin-processor`. Press Enter.
4. While it works, **read every request before approving it**:
   - **Approve:** commands and reads inside `~/charm-rerun/A`; `gh api` and
     `gh search` calls on `<ORG>/...` or with `--owner <ORG>` /
     `org:<ORG>`; GitHub MCP calls on the same organization; web
     searches; writes to `~/charm-rerun/A/outputs/`.
   - **Reject** (and write each one in the run record):
     - reading anything outside `~/charm-rerun/A`, in particular `~/.cursor`,
       chat or agent transcripts, `~/charm-kit-rerun`, `~/charm-archive` and
       your home folder;
     - anything on `socrateslopes/...`, and searches for the study, the
       thesis or the paper;
     - GitHub searches without an organization or repository limit, and
       listing your own repositories;
     - `git clone`; building, installing or running code; MCP tools other
       than GitHub's.
   - Send **M1** or **M2** only when needed.

   If the chat is summarized and the agent then asks to read its transcript,
   reject it. That is what invalidated the first runs.
5. When it finishes, click **Keep all** if Cursor shows pending changes.
6. Check the output and move it to the results folder:
   ```bash
   python3 -m json.tool ~/charm-rerun/A/outputs/<service>.json > /dev/null && echo JSON-OK
   mv ~/charm-rerun/A/outputs/<service>.json ~/charm-rerun/A/outputs/<service>.log.md ~/charm-kit-rerun/execution-rerun/results/A/
   ```
   If the JSON is invalid, do not fix it; write it in the run record.
7. Export the chat to
   `~/charm-kit-rerun/execution-rerun/results/A/chat_<service>.md`.
8. Scroll through the chat. The run is **invalid** if the agent read local
   files outside the workspace **without asking you**, used an MCP server
   other than GitHub's, or read the study's materials. Then delete its
   results, write it under *Deviations* in `environment.md`, and repeat the
   chat **once**. If the second attempt is also invalid, keep it, record it,
   and go on: we will disclose it instead of repeating again.
9. Finish the run record. Fill in **every** field, including the list of
   calls you approved to GitHub and the calls you rejected.

**After both services:**

```bash
python3 ~/charm-kit-rerun/execution/tools/check_evidence.py ~/charm-rerun/A ~/charm-kit-rerun/execution-rerun/results/A
cd ~/charm-kit-rerun && git add execution-rerun && git commit -m "Rerun of Task A (payin-processor, agents-commissions)" && git push
```

## Part 4. Build workspace B1 (~5 min)

1. Close the A folder in Cursor and delete workspace A:
   ```bash
   rm -rf ~/charm-rerun/A
   ```
2. Download the B inputs and build the workspace: the B0 inputs as before,
   plus the corrected developer input.
   ```bash
   cd ~/charm-kit-rerun && git pull && git sparse-checkout add /execution-b/B0-inputs/ /execution-rerun-b/
   mkdir -p ~/charm-rerun/B1/outputs
   cp -R ~/charm-kit-rerun/execution-b/B0-inputs ~/charm-rerun/B1/inputs
   cp -R ~/charm-kit-rerun/execution-rerun-b/B1-inputs/developer-input ~/charm-rerun/B1/inputs/developer-input
   ls ~/charm-rerun/B1/inputs/developer-input/interviews      # must list P1.md to P7.md
   cd ~/charm-rerun/B1 && find inputs -type f -exec shasum -a 256 {} \; | sort -k2 > ~/charm-kit-rerun/execution-rerun/results/B1/input-checksums.txt
   cat ~/charm-kit-rerun/execution-rerun/results/B1/input-checksums.txt
   ```
3. Send me the checksum list if you want me to confirm that only P4.md and
   P5.md differ from the first B1 run (or skip this; I will check it when
   scoring).
4. In Cursor: *File → Open Folder…* → `~/charm-rerun/B1`.

## Part 5. Run B1 (1 chat)

1. Run record:
   `cp ~/charm-kit-rerun/execution/templates/run-record.md ~/charm-kit-rerun/execution-rerun/results/B1/run-record.md`
2. New chat, **Agent** mode, the same model. Paste everything below the `---`
   line of `~/charm-kit-rerun/execution/prompts/B1-assessment.md` (nothing
   to fill in). Press Enter.
3. Same rules as Part 3, steps 4, 5, 8 and 9, with `~/charm-rerun/B1` as the
   workspace.
4. Check and move the output:
   ```bash
   python3 -m json.tool ~/charm-rerun/B1/outputs/assessment.json > /dev/null && echo JSON-OK
   mv ~/charm-rerun/B1/outputs/* ~/charm-kit-rerun/execution-rerun/results/B1/
   ```
5. Export the chat to `~/charm-kit-rerun/execution-rerun/results/B1/chat.md`.

## Part 6. Report back

1. Finish `execution-rerun/results/environment.md` (deviations and
   impressions) and commit:
   ```bash
   cd ~/charm-kit-rerun && git add execution-rerun && git commit -m "Rerun of Task B1 and report" && git push
   ```
2. Tell the researcher who scores the runs that the results are in the repository.
3. Optional: delete `~/charm-rerun`, `~/charm-kit-rerun` and
   `~/charm-archive` from the execution computer.

---

## If something goes wrong

| Situation | What to do |
|---|---|
| `rebuild_snapshot.py` fails to clone a repository | Check that `git clone` works for it in Terminal with your account (SSH key or `gh auth setup-git`), then delete `~/charm-rerun/A` and run Part 2 again. |
| It says a folder "already exists" | Delete `~/charm-rerun/A` and run Part 2 again. |
| Cursor runs commands without asking | Auto-run is not set to "Ask every time". Stop the chat, fix the setting, delete the outputs and start a new chat. |
| The agent read a file outside the workspace without asking | See Part 3, step 8 (repeat once, then keep and disclose). |
| You typed something other than M1 or M2 | The run is invalid: delete its outputs and repeat it; note it. |
| The prompt checksums differ from the expected ones | Stop and report it. |
