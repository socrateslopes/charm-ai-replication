# Open checks (protocol Section 11, deviations 7, 8 and 9)

Three checks that only the researcher can do. Do them in order, one at a
time. After each one, commit and tell Claude "Check N done"; Claude will
score it and update the paper.

| Check | What you judge | Time | Needs |
|---|---|---|---|
| 1. Citations | Do the cited code lines support what the agent claimed? (100 items) | ~30 min setup + ~45 min | A computer with access to the company's GitHub organization |
| 2. Drawbacks | Is each drawback the agents gave for a recommended pattern also in the book? (59 drawbacks, 9 patterns) | ~1 h | The book (Brown, Woolf and Yoder), chapters 4–6; Joe can help |
| 3. Extra patterns | Are the 5 patterns the agents added (beyond what participants named) really in the system? | ~30 min | Your knowledge of the system, the code if needed |

---

## Check 1. Do the citations support the claims?

**Done 2026-10-02** by the researcher: 93 yes, 5 partly, 2 no
(`results/check1-citations.csv`).

The automatic check showed that 1,189 of 1,192 cited locations exist. This
check asks whether they say what the agent claims. A script picks 20 items per
service at random (fixed seed, so the sample is reproducible), shows each item
next to the code lines it cites, and records your answer. It writes only your
verdicts, never code.

No isolation is needed any more, so use your usual computer.

1. Update the repository and rebuild the snapshot (same tool and commits as
   the rerun; 20–40 min):
   ```bash
   cd <your jise clone> && git pull
   python3 execution-rerun/tools/rebuild_snapshot.py execution/results/snapshots.csv \
       ~/charm-check/A /tmp/charm-check-manifest.csv
   ```
   It must end with `OK`.
2. Run the check:
   ```bash
   python3 experiment/checks/check_citations.py ~/charm-check/A
   ```
   For each item it shows the service, the question (e.g. "Q4 outgoing call"),
   the item, the agent's note and the cited lines (marked `>>`, with 3 lines
   of context). Answer:
   - `y`: the lines support the item;
   - `p`: partly (e.g. right place, but they show only part of the claim, or
     the claim needs a second file to be confirmed);
   - `n`: they do not support it;
   - `s`: you cannot judge.

   Add a short note for every `p` and `n`. You can stop with Ctrl+C and run
   the same command later: answered items are skipped.
3. Commit the verdicts and delete the snapshot:
   ```bash
   git add experiment/checks/results/check1-citations.csv && git commit -m "Check 1: citations" && git push
   rm -rf ~/charm-check /tmp/charm-rerun-clones
   ```

## Check 2. Are the drawbacks documented in the book?

**Done 2026-10-02** by Claude from the full text of chapters 4–6, at the
researcher's request (protocol Section 11, deviation 8). Each row has the
verdict, the section and the supporting passage. A spot-check by the
researcher or Joe is still recommended; the steps below are kept for it.

The protocol counts how many of the drawbacks the agents listed for each
recommended pattern are documented in Brown, Woolf and Yoder. The catalog the
agents saw had no drawbacks, so this needs the book.

1. Open `experiment/checks/check2-drawbacks.csv` in a spreadsheet. It has one
   row per drawback, sorted by chapter and pattern, so you read each pattern's
   section once.
2. For each row, fill in:
   - `documented`: `yes` if the book states the same drawback in substance
     (in the pattern's consequences, liabilities, or text), `partly` if it
     mentions a related or more general concern, `no` if not;
   - `where`: chapter and page or section;
   - `note`: optional.

   Drawbacks that are about this system rather than the pattern (e.g. "owned
   by other teams") will usually be `no`; that is expected.
3. Save it as CSV with the same name and commit:
   ```bash
   git add experiment/checks/check2-drawbacks.csv && git commit -m "Check 2: drawbacks" && git push
   ```

### Spot-check of Claude's verdicts (~20 min)

Check 2 was judged by Claude, so a person confirms a sample: 15 of the 59
verdicts (5 yes, 5 partly, 5 no, fixed seed). Keep the book open at the
section each row shows.

```bash
python3 experiment/checks/spot_check_drawbacks.py
git add experiment/checks/results/check2-spotcheck.csv && git commit -m "Spot-check of check 2" && git push
```

Answer `a` (agree), `d` (disagree, then give your verdict) or `s` (skip).

**Done 2026-10-03:** 14 of 15 agreed; B1-R1-D6 changed from partly to no.

## Check 3. Are the extra patterns really in the system?

**Done 2026-10-03** by the researcher: 1 supported, 2 partly, 2 unsupported.

Open `experiment/checks/check3-extra-patterns.md`. For each of the five
patterns it gives the catalog definition, what the agents argued, and where to
look (pointers taken from the Task A results). Fill in the verdict lines
(supported / partly / unsupported, and the services) directly in the file,
then commit:

```bash
git add experiment/checks/check3-extra-patterns.md && git commit -m "Check 3: extra patterns" && git push
```

You can also edit the file on GitHub or in Overleaf (it syncs with the
repository).
