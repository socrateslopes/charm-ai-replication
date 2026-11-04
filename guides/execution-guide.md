# Experiment execution: start here

*Guide used for the first execution (2026-09-30 to 10-01), kept as it was
used apart from removing names. Paths refer to the private repository layout
(see the top-level README).*

This folder holds everything needed to run the experiment, and the results
are committed back into it. Follow the parts in order. Commands are for
macOS or Linux (Terminal).

**Layout of the repository for the experiment**

| Folder | Content | When it is on the execution computer |
|---|---|---|
| `execution/prompts/` | The four prompts to paste into Cursor | From Part 1 |
| `execution/tools/` | Snapshot, evidence-check and transcript scripts | From Part 1 |
| `execution/templates/` | `environment.md` (your report) and `run-record.md` | From Part 1 |
| `execution/A-inputs/` | Questionnaire and list of services for Task A | From Part 1 |
| `execution/results/` | Where every output, chat and record is committed | From Part 1 |
| `execution-b/` | Inputs for Tasks B0 and B1 (they include the answer key of Task A) | **Only from Part 5** |
| `transcripts-raw/` | Raw interview transcripts (git-ignored) | **Never** |

Everything else in the repository (the paper, the protocol) describes the
answer keys and must **not** be on the execution computer. Part 1 uses a
sparse checkout so that only `execution/` is downloaded.

**Already prepared:** cutoff date (2026-03-11), the list of services with
their real names, the three characterization tables, the service
descriptions, the developers' comments, and the pattern catalog.

**Runs:** one chat per service for Task A (5 chats), one chat for B0 and one
for B1, plus the preparation chat P0.

**Tool policy (all chats):** the agent may use its built-in tools (files,
search, terminal), GitHub (the GitHub MCP server and `gh`) and the internet
(web search). **No other MCP server is allowed**: disable all of them in
Part 1. The prompts also forbid the agent to look for this study, and in
Task A to read GitHub code newer than the cutoff.

**Protecting the answer keys.** `jise`, `masters-2026` and `asian-plop` are
private, but the agent can reach them through *your* GitHub account. Web
search cannot see private repositories, so the only way in is a GitHub call
made with your credentials. Therefore:

- Cursor must ask for your approval before **every** terminal command and
  MCP tool call (Part 1).
- You reject any call that touches `socrateslopes/...` or looks for the
  study, the thesis or the paper.
- You reject any GitHub **search** that is not limited to the company's
  organization (`org:<organization>`). An unlimited search can return
  content from your private repositories even if it does not name them.

**The two standard messages** (the only things you may type into an A, B0 or
B1 chat besides the prompt, each at most twice per chat):

- **M1**, if the agent asks a question:
  `Proceed with your best judgment, following the rules in the task, and record your assumptions.`
- **M2**, if the agent stops before writing its output files:
  `Continue until all required outputs are written.`

---

## Part 0. Prepare the transcripts (your usual computer, ~20 min)

1. Clone or pull the `jise` repository on your usual computer and open a
   Terminal at its root.
2. Create the folder `transcripts-raw/` at the root (it is git-ignored).
3. For each interview document, open its **Transcrição** tab and use
   *File → Download → Plain text (.txt)*. Save it in `transcripts-raw/` with
   the name below. If the downloaded file has no timestamps (`00:12:34`),
   copy the whole Transcrição tab and paste it into the `.txt` file instead.

   | File | Document |
   |---|---|
   | `P1.txt` | P1 Caracterização dos serviços: Payin Processor - 2026/03/11 14:00 |
   | `P2.txt` | P2 Caracterização dos serviços: Agents Commissions - 2026/03/11 15:28 |
   | `P3.txt` | P3 Caracterização dos serviços: Payout Processor - 2026/03/11 16:31 |
   | `P4.txt` | P4 Caracterização dos serviços: Credit Card Processor - 2026/03/11 17:23 |
   | `P5.txt` | P5 Caracterização de serviços: Bank Interface - 2026/03/12 16:09 |
   | `P6.txt` | P6 Caracterização de serviços: Payin Processor - 2026/03/12 17:03 |
   | `P7.txt` | P7 Caracterização de serviços do Payout - 2026/03/13 10:55 |

4. Run:
   ```bash
   python3 execution/tools/prepare_transcripts.py transcripts-raw \
       execution-b/B1-inputs/developer-input/interviews \
       --interviewer "Sócrates Lopes" --remove "<COMPANY>" --remove "<COMPANY>" \
       --report execution/results/transcript-cuts.csv
   ```
   For each participant, the script shows where it thinks the pattern part
   of the interview begins and asks **"Cut here?"**. If the marked line is
   where you started the pattern part, press Enter. Press `n` for the next
   suggestion, or `t` to type the timestamp yourself.

   If a file stops with **"could not find the participant's speaker
   label"**, the script prints the speaker labels it found. Then add one of
   these options to the command in step 4 and run it again:
   - `--participant P7="<label>"` if the participant is one of the printed
     labels;
   - `--unattributed P7` if all the speech is under one name (the recording
     did not separate the speakers). Every turn is then labeled "Speaker".

   `--list-speakers` prints the labels of all files without writing
   anything.
5. Open each `execution-b/B1-inputs/developer-input/interviews/P<n>.md` and
   check that:
   - the last lines are still about the characterization, not patterns;
   - no personal names remain. If some do, add `--remove "<name>"` and run
     step 4 again.
6. Delete the raw files and commit:
   ```bash
   rm -rf transcripts-raw
   git add execution-b/B1-inputs/developer-input/interviews execution/results/transcript-cuts.csv
   git commit -m "Add anonymized interview excerpts for B1"
   git push
   ```

## Part 1. Prepare the execution computer (~30 min)

1. Use a computer account that has never been used for this research.
2. Download only the `execution/` folder (sparse checkout):
   ```bash
   git clone --filter=blob:none --no-checkout <URL of this repository> ~/charm-kit
   cd ~/charm-kit
   git sparse-checkout set execution
   git checkout main
   ls ~/charm-kit        # must show only: execution
   mkdir -p ~/charm-study
   ```
3. Start your report and record the prompt checksums:
   ```bash
   cd ~/charm-kit
   cp execution/templates/environment.md execution/results/environment.md
   shasum -a 256 execution/prompts/*
   ```
   Paste the checksums into `execution/results/environment.md`.
4. Install Cursor (cursor.com), or use an installation with no history for
   this research, and sign in. In **Cursor Settings** (`Cmd/Ctrl+Shift+J`;
   names vary between versions):
   - **Privacy Mode**: on.
   - **Rules**: delete all User Rules.
   - **Memories**: off; delete any existing ones.
   - **Background agents**: off.
   - **Model**: choose one model explicitly (recommended: the most capable
     Claude model listed), never "Auto". Keep the same model, "Max" mode
     and thinking settings for all chats.
   - **Web search**: on.
   - **Auto-run** (sometimes "YOLO mode"): off, so that every terminal
     command **and every MCP tool call** asks for approval ("Ask every
     time"; an empty allowlist also works). Do not use "Run everything".
   - **MCP**: disable every MCP server except GitHub's (*Settings → MCP* or
     *Tools & Integrations*). If no GitHub MCP server is installed, that is
     fine: the agent can use `gh` in the terminal.
5. Fill in the first rows of `execution/results/environment.md` (computer,
   Cursor version, model, settings, MCP servers enabled).

## Part 2. Locate and snapshot the code (P0, ~15–30 min)

The agent finds the repositories by the service names and copies them as
they were on March 11, 2026, without git history.

1. Check GitHub access in Terminal (`gh auth status`), or that a GitHub MCP
   server is enabled in Cursor.
2. In Cursor: *File → Open Folder…* → `~/charm-kit`.
3. New chat (`Cmd/Ctrl+L`, then `+`), **Agent** mode, the chosen model.
4. Open `execution/prompts/P0-locate-and-snapshot.md`, copy everything below
   the `---` line, paste it into the chat, and replace
   `<GitHub organization ...>` with your organization. Press Enter. Approve
   the commands it needs (`gh`, `git`, `bash .../snapshot.sh`, `find`, `du`).
5. When it finishes, review `execution/results/repo-map.csv`: does each
   service include its own code, workers, deployment and infrastructure, and
   nothing from other teams? If something is missing or wrong, ask the agent
   in the same chat to fix it, and write what you asked in `environment.md`.
6. Check that `execution/A-inputs/services.csv` now has `code_locations` for
   all five services.
7. Export the chat to `execution/results/chat_P0.md` (chat menu `…` →
   Export; or select all, copy and paste).
8. Close the folder (*File → Close Folder*).

## Part 3. Build workspace A

1. **Optional but stronger:** if you have another GitHub account that
   belongs to the company's organization and is **not** a collaborator on
   `socrateslopes/jise`, `masters-2026` or `asian-plop` (for example, a work
   account), log the agent's tools in with it for A, B0 and B1:
   - `gh auth logout`, then `gh auth login` with that account;
   - in Cursor, give the GitHub MCP server a token from that account.

   Check it with
   `gh api repos/socrateslopes/jise --silent && echo VISIBLE || echo "OK: not visible"`.
   Otherwise keep your account and rely on approving calls by hand (see
   *Protecting the answer keys* above). Either way, write in
   `environment.md` which account the agent used.
2. Check that Cursor lists no MCP server other than GitHub's and that
   auto-run is off.
3. In Terminal:
   ```bash
   mkdir -p ~/charm-study/A/inputs ~/charm-study/A/outputs
   cp ~/charm-kit/execution/A-inputs/questionnaire.md ~/charm-kit/execution/A-inputs/services.csv ~/charm-study/A/inputs/
   cp ~/charm-kit/execution/results/snapshots.csv ~/charm-study/A/inputs/
   ```
4. In Cursor: *File → Open Folder…* → `~/charm-study/A`. Wait until
   indexing finishes.

## Part 4. Run Task A (5 chats)

One chat per service, in this order: `payin-processor`, `credit-card-processor`, `agents-commissions`,
`bank-interface`, `payout-processor`.

**For each service:**

1. Create the run record and write the start time in it:
   ```bash
   cp ~/charm-kit/execution/templates/run-record.md ~/charm-kit/execution/results/A/run-record_<service>.md
   ```
2. New chat (`+`), **Agent** mode, the chosen model.
3. Open `~/charm-kit/execution/prompts/A-characterization.md`, copy
   everything below the `---` line, paste it into the chat, and change only
   the first line, e.g. `SERVICE_ID: payin-processor`. Press Enter.
4. While it works:
   - read every call before approving it;
   - approve local commands that read files inside the workspace, GitHub
     reads of the company's organization (GitHub MCP tools, `gh api`), and
     GitHub searches limited to it (`org:<organization>` or
     `repo:<organization>/...`);
   - reject the following, and write each rejection in the run record:
     - `git clone`, and any `git` command on `~/charm-kit`;
     - anything that touches `socrateslopes/...` or looks for the study,
       the thesis or the paper;
     - GitHub searches without an `org:` or `repo:` limit, and listing your
       own repositories (for example `gh repo list` with no organization);
     - any MCP tool that is not GitHub's;
     - building, installing or running code;
     - reading local files outside `~/charm-study/A`;
   - send **M1** or **M2** only when needed.
5. When it finishes, click **Keep all** (or **Accept all**) if Cursor shows
   pending changes.
6. Check the output, then move it to the results folder:
   ```bash
   python3 -m json.tool ~/charm-study/A/outputs/<service>.json > /dev/null && echo JSON-OK
   mv ~/charm-study/A/outputs/<service>.json ~/charm-study/A/outputs/<service>.log.md ~/charm-kit/execution/results/A/
   ```
   If the JSON is invalid, do not fix it; write it in the run record.
7. Export the chat to `~/charm-kit/execution/results/A/chat_<service>.md`.
8. Scroll through the chat. The run is **invalid** if the agent:
   - used an MCP server other than GitHub's;
   - read the study's materials (`socrateslopes/...`, the thesis, the
     paper); or
   - read local files outside the workspace.

   Then delete its results, write it under *Deviations* in
   `environment.md`, and repeat the chat.

   If it read GitHub code newer than the cutoff, the run stays valid: write
   it in the run record. In every case, list in the run record the GitHub
   repositories and web pages it consulted (its log should list them too).
9. Finish the run record (end time, M1/M2 counts, rejections, usage shown
   by Cursor, anything unusual).

If `git push` fails because the agent's tools use another GitHub account
(Part 3, step 1), keep the commits local and push them in Part 9.

**After the five services:**

```bash
python3 ~/charm-kit/execution/tools/check_evidence.py ~/charm-study/A ~/charm-kit/execution/results/A
cd ~/charm-kit && git add execution && git commit -m "Task A results" && git push
```

## Part 5. Build workspace B0

1. Close the A folder in Cursor and delete workspace A:
   ```bash
   rm -rf ~/charm-study/A
   ```
2. Download the B inputs and build the workspace:
   ```bash
   cd ~/charm-kit && git pull && git sparse-checkout add execution-b
   mkdir -p ~/charm-study/B0/outputs
   cp -R ~/charm-kit/execution-b/B0-inputs ~/charm-study/B0/inputs
   cd ~/charm-study/B0 && find inputs -type f -exec shasum -a 256 {} \; | sort -k2 > ~/charm-kit/execution/results/B0/input-checksums.txt
   ```
3. In Cursor: *File → Open Folder…* → `~/charm-study/B0`.

## Part 6. Run B0 (1 chat)

1. Run record: `cp ~/charm-kit/execution/templates/run-record.md ~/charm-kit/execution/results/B0/run-record.md`
2. New chat, **Agent** mode, the chosen model. Paste everything below the
   `---` line of `~/charm-kit/execution/prompts/B0-assessment.md` (nothing to
   fill in). Press Enter.
3. Same rules as Part 4, steps 4, 5, 8 and 9, with `~/charm-study/B0` as
   the workspace.
4. Check and move the output:
   ```bash
   python3 -m json.tool ~/charm-study/B0/outputs/assessment.json > /dev/null && echo JSON-OK
   mv ~/charm-study/B0/outputs/* ~/charm-kit/execution/results/B0/
   ```
5. Export the chat to `~/charm-kit/execution/results/B0/chat.md`, then
   commit:
   ```bash
   cd ~/charm-kit && git add execution && git commit -m "Task B0 results" && git push
   ```

## Part 7. Build workspace B1

1. Close the B0 folder in Cursor, then:
   ```bash
   mkdir -p ~/charm-study/B1/outputs
   cp -R ~/charm-study/B0/inputs ~/charm-study/B1/inputs
   rm -rf ~/charm-study/B0
   cp -R ~/charm-kit/execution-b/B1-inputs/developer-input ~/charm-study/B1/inputs/developer-input
   rm -f ~/charm-study/B1/inputs/developer-input/interviews/.gitkeep
   ls ~/charm-study/B1/inputs/developer-input/interviews     # must list P1.md to P7.md
   cd ~/charm-study/B1 && find inputs -type f -exec shasum -a 256 {} \; | sort -k2 > ~/charm-kit/execution/results/B1/input-checksums.txt
   grep -v developer-input ~/charm-kit/execution/results/B1/input-checksums.txt | diff - ~/charm-kit/execution/results/B0/input-checksums.txt && echo SAME-AS-B0
   ```
2. In Cursor: *File → Open Folder…* → `~/charm-study/B1`.

## Part 8. Run B1 (1 chat)

As Part 6, with `B1-assessment.md`, the folder `~/charm-study/B1` and the
results folder `~/charm-kit/execution/results/B1/`. Commit with the message
`Task B1 results`.

## Part 9. Report back

1. Finish `execution/results/environment.md` (deviations and impressions)
   and commit everything that is left:
   ```bash
   cd ~/charm-kit && git add execution && git commit -m "Experiment report"
   gh auth login          # your own account again, if you switched in Part 3
   git push
   ```
2. Tell the researcher who scores the runs that the results are in the
   repository.
3. Optional: delete `~/charm-study` and `~/charm-kit` from the execution
   computer.

---

## If something goes wrong

| Situation | What to do |
|---|---|
| The agent wants to edit files outside `outputs/` | Reject; note it in the run record. |
| The agent searches GitHub or the web for the study, the thesis or the paper | Reject. If it read any of them, the run is invalid: repeat it. |
| Cursor runs a command or MCP tool without asking you | Auto-run is on. Stop the chat, turn it off, check whether the agent touched your private repositories, and repeat the run if it did. |
| The chat errors out or runs out of context | Delete partial outputs; repeat the run in a new chat; note it under Deviations. |
| Cursor's usage limit is reached | Wait. Do not change the model. |
| You typed something other than M1 or M2 | The run is invalid: delete its outputs, repeat it, note it. |
| JSON invalid or incomplete after two M2 | Keep it as it is and note it. It is a result. |
| `git sparse-checkout` is not available | Update git (version 2.25 or later). |
| You find a mistake in an input after some runs | Stop, report it, and note it. Those runs will probably need repeating. |
