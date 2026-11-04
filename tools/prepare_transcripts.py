#!/usr/bin/env python3
"""Cut and anonymize interview transcripts for condition B1.

For each raw transcript (P1.txt ... P7.txt, plain text or Markdown exported
from the meeting-notes documents), this script:

  1. keeps only the transcript itself (drops any summary before the first
     timestamp and anything after "A transcrição foi encerrada" / "Tab 3");
  2. finds the interviewer turn that starts the pattern stage (part 3) and
     cuts the transcript right BEFORE it, asking you to confirm the cut;
  3. replaces speaker names with "Interviewer" and "P<n>", replaces the
     names in the text (including close misspellings), and removes e-mails,
     links and any extra terms you pass with --remove;
  4. writes <output_dir>/P<n>.md and a report of the cuts (--report).

Usage (run it on your usual computer, NOT on the execution computer):

    python3 prepare_transcripts.py <raw_dir> <output_dir> \
        --interviewer "Sócrates Lopes" --remove "Some Company" --remove "XYZ" \
        --report transcript-cuts.csv

Options:
    --cut P3=00:31:10   force the cut at the first interviewer turn at or after
                        this timestamp (repeatable); skips the question.
    --yes               accept the suggested cut without asking (not
                        recommended: check the printed context).
    --list-speakers     only print, for each file, the speaker labels found
                        and how many turns each has, then stop. Use it when
                        a file fails with "could not find the participant".
    --participant P7="Label"
                        use this speaker label (exactly as printed by
                        --list-speakers) as the participant (repeatable).
    --unattributed P7   the transcript does not separate the speakers (for
                        example, everything is under one name): keep all
                        turns, label them "Speaker", and let any turn be the
                        cut point (repeatable).
    --report FILE       where to write the CSV report of the cuts
                        (default: transcript-cuts.csv).
"""
import argparse
import csv
import difflib
import re
import sys
import unicodedata
from pathlib import Path

TS_LINE = re.compile(r"^\W*(\d{1,2}:\d{2}:\d{2})\W*$")
END_MARKERS = re.compile(r"transcri[cç][aã]o foi encerrada|^\W*tab \d+\W*$|confirmed mentions of charm", re.I)
TURN = re.compile(r"^\s*\**\s*(?P<name>[^\W\d_][^:*\n,.?!;]{1,70}?)\s*\**\s*:\s*\**\s*(?P<text>.*)$")
# Phrases with which the interviewer opens the pattern stage, strongest first.
STRONG = [r"terceira (etapa|parte)", r"(etapa|parte|fase) (dos|de|sobre) padr", r"cat[aá]logo",
          r"comp[eê]ndio", r"livro", r"lista de padr", r"padr[õo]es (de|do|da|para) (arquitetura|microsservi|design|comunica)"]
WEAK = [r"padr[õo]es"]
PARTICLES = {"dos", "das", "del", "von", "van", "der"}
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
URL = re.compile(r"(https?://\S+|www\.\S+)")


def norm(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z ]", "", s).strip()


def parse(text):
    lines = text.replace("\ufeff", "").replace("\r\n", "\n").replace("\r", "\n").split("\n")
    start = next((i for i, l in enumerate(lines) if TS_LINE.match(l)), None)
    if start is None:
        raise ValueError("no timestamp line (hh:mm:ss) found")
    items, ts = [], TS_LINE.match(lines[start]).group(1)
    for line in lines[start:]:
        if END_MARKERS.search(line):
            break
        if not line.strip():
            continue
        m = TS_LINE.match(line)
        if m:
            ts = m.group(1)
            items.append(("ts", ts, None))
            continue
        m = TURN.match(line)
        if m and len(m.group("name").split()) <= 10 and not re.search(r"https?", m.group("name")):
            items.append(("turn", ts, [m.group("name").strip(), m.group("text").strip()]))
        elif items and items[-1][0] == "turn":
            items[-1][2][1] += " " + line.strip()
    return items


def candidates(items, is_interviewer):
    turns = [(i, it) for i, it in enumerate(items) if it[0] == "turn" and is_interviewer(it[2][0])]
    found = []
    for pats in (STRONG, WEAK):
        for i, it in turns:
            if any(re.search(p, it[2][1], re.I) for p in pats) and i not in [c[0] for c in found]:
                found.append((i, it))
    return found


def show(items, idx, n=3):
    lo = max(0, idx - n)
    for j in range(lo, min(len(items), idx + n + 1)):
        kind, ts, turn = items[j]
        mark = ">>" if j == idx else "  "
        if kind == "ts":
            print(f"{mark} [{ts}]")
        else:
            print(f"{mark} {turn[0]}: {turn[1][:220]}")


def to_seconds(ts):
    h, m, s = (int(x) for x in ts.split(":"))
    return h * 3600 + m * 60 + s


def choose_cut(pid, items, is_interviewer, forced, auto):
    if forced:
        for i, it in enumerate(items):
            if it[0] == "turn" and is_interviewer(it[2][0]) and to_seconds(it[1]) >= to_seconds(forced):
                return i
        raise ValueError(f"{pid}: no interviewer turn at or after {forced}")
    cands = candidates(items, is_interviewer)
    k = 0
    while True:
        if k >= len(cands):
            ts = input(f"{pid}: no (more) suggestions. Type the timestamp hh:mm:ss of the turn that starts the pattern stage: ").strip()
            return choose_cut(pid, items, is_interviewer, ts, auto)
        i = cands[k][0]
        print(f"\n=== {pid}: suggested cut before the marked turn (at {items[i][1]}) ===")
        show(items, i)
        if auto:
            return i
        ans = input("Cut here? [Enter = yes / n = next suggestion / t = type a timestamp]: ").strip().lower()
        if ans == "":
            return i
        if ans == "t":
            return choose_cut(pid, items, is_interviewer, input("Timestamp hh:mm:ss: ").strip(), auto)
        k += 1


def anonymizer(names_to_labels, removes):
    def fuzzy_word(word):
        w = norm(word)
        if len(w) < 3:
            return None
        for name, label in names_to_labels:
            for part in name.split():
                if len(part) == 3 and w == part and part not in PARTICLES:
                    return label
                if len(part) >= 4 and len(w) >= 4 and difflib.SequenceMatcher(None, w, part).ratio() >= 0.8:
                    return label
        return None

    def apply(text):
        text = EMAIL.sub("[e-mail]", URL.sub("[link]", text))
        for term in removes:
            text = re.sub(r"(?<!\w)" + re.escape(term) + r"(?!\w)", "[company]", text, flags=re.I)
        out = []
        for tok in re.split(r"(\W+)", text):
            label = fuzzy_word(tok) if tok[:1].isupper() else None
            out.append(label if label else tok)
        text = "".join(out)
        for label in {l for _, l in names_to_labels}:  # "P2 P2" -> "P2"
            text = re.sub(rf"\b{label}(\s+{label})+\b", label, text)
        return text
    return apply


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("raw_dir")
    ap.add_argument("output_dir")
    ap.add_argument("--interviewer", required=True)
    ap.add_argument("--remove", action="append", default=[])
    ap.add_argument("--cut", action="append", default=[])
    ap.add_argument("--yes", action="store_true")
    ap.add_argument("--list-speakers", action="store_true")
    ap.add_argument("--participant", action="append", default=[])
    ap.add_argument("--unattributed", action="append", default=[])
    ap.add_argument("--report", default="transcript-cuts.csv")
    a = ap.parse_args()
    forced = {k.upper(): v for k, v in (c.split("=", 1) for c in a.cut)}
    chosen = {k.strip().upper(): v.strip().strip('"') for k, v in (c.split("=", 1) for c in a.participant)}
    unattributed = {u.strip().upper() for u in a.unattributed}
    interviewer = norm(a.interviewer).split()[0]
    out = Path(a.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    report = []
    files = sorted(p for p in Path(a.raw_dir).iterdir() if re.match(r"P\d+\.(txt|md)$", p.name, re.I))
    if not files:
        sys.exit(f"No P<n>.txt or P<n>.md files in {a.raw_dir}")
    for f in files:
        pid = f.stem.upper()
        items = parse(f.read_text(encoding="utf-8", errors="replace"))
        speakers = {}
        for it in items:
            if it[0] == "turn":
                speakers[it[2][0]] = speakers.get(it[2][0], 0) + 1
        if a.list_speakers:
            n_ts = sum(1 for it in items if it[0] == "ts")
            print(f"{pid}: {n_ts} timestamps, {sum(speakers.values())} turns")
            for s, n in sorted(speakers.items(), key=lambda x: -x[1]):
                role = "interviewer" if norm(s).startswith(interviewer) else "other"
                print(f"    {n:5d}  {s!r}  ({role})")
            continue
        if pid in unattributed:
            label_of = {s: "Speaker" for s in speakers}
            is_interviewer = lambda name: True
        else:
            if pid in chosen:
                if chosen[pid] not in speakers:
                    sys.exit(f"{pid}: speaker label {chosen[pid]!r} not found; run with --list-speakers")
                participant = chosen[pid]
            else:
                others = sorted((s for s in speakers if not norm(s).startswith(interviewer)), key=lambda s: -speakers[s])
                if not others:
                    found = ", ".join(f"{s!r} ({n} turns)" for s, n in sorted(speakers.items(), key=lambda x: -x[1])) or "none"
                    sys.exit(
                        f"{pid}: could not find the participant's speaker label.\n"
                        f"  Speaker labels found: {found}\n"
                        f"  - If the participant is one of them, add: --participant {pid}=\"<label>\"\n"
                        f"  - If all the speech is under one label (speakers not separated), add: --unattributed {pid}\n"
                        f"  - If no labels were found, the file has another layout: run with --list-speakers and\n"
                        f"    describe to Claude how the lines look (without copying their content).")
                participant = others[0]
            label_of = {s: "Interviewer" for s in speakers if norm(s).startswith(interviewer) and s != participant}
            label_of[participant] = pid
            for extra in speakers:
                label_of.setdefault(extra, "Other")
            if "Interviewer" not in label_of.values():
                sys.exit(f"{pid}: no interviewer turns left; if the speakers are not separated, use --unattributed {pid}")
            is_interviewer = lambda name, lo=label_of: lo.get(name) == "Interviewer"
        cut = choose_cut(pid, items, is_interviewer, forced.get(pid), a.yes)
        kept = items[:cut]
        while kept and kept[-1][0] == "ts":  # drop a dangling timestamp heading
            kept.pop()
        names = [(norm(a.interviewer), "Interviewer" if pid not in unattributed else "Speaker")] + \
                [(norm(s), l) for s, l in label_of.items() if l not in ("Interviewer", "Speaker")]
        anon = anonymizer(names, a.remove)
        lines = [f"# Interview {pid} (excerpt: profile and evaluation of the characterization)"]
        if pid in unattributed:
            lines += ["", "The original transcript does not separate the speakers; every turn is labeled \"Speaker\"."]
        for kind, ts, turn in kept:
            if kind == "ts":
                lines += ["", f"### {ts}", ""]
            else:
                lines.append(f"{label_of.get(turn[0], 'Other')}: {anon(turn[1])}")
        (out / f"{pid}.md").write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
        n_turns = sum(1 for it in items if it[0] == "turn")
        n_kept = sum(1 for it in kept if it[0] == "turn")
        report.append({"participant": pid, "cut_before_turn_at": items[cut][1], "turns_kept": n_kept,
                       "turns_removed": n_turns - n_kept,
                       "speakers_separated": "no" if pid in unattributed else "yes",
                       "other_speakers": sum(1 for l in label_of.values() if l == "Other")})
        print(f"{pid}: kept {n_kept} of {n_turns} turns, cut at {items[cut][1]} -> {out / (pid + '.md')}")
    if a.list_speakers:
        return
    rep = Path(a.report)
    with rep.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(report[0]))
        w.writeheader()
        w.writerows(report)
    print(f"\nReport: {rep}")
    print("Now open each P<n>.md, check the last lines (no pattern discussion) and search for any remaining personal names.")


if __name__ == "__main__":
    main()
