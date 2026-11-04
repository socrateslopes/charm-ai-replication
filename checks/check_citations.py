#!/usr/bin/env python3
"""Check 1: does the cited code support the item? (protocol Section 9.1)

Draws a fixed random sample of 20 items per service from the final Task A
results (reruns for payin-processor and agents-commissions, first execution for the others),
shows each item and the code lines it cites from the snapshot, and records
your verdict. Only verdicts and notes are written, never code.

Usage (from the root of the jise repository):
    python3 experiment/checks/check_citations.py <snapshot_workspace>
Example:
    python3 experiment/checks/check_citations.py ~/charm-check/A

Verdicts: y = the lines support the item; p = partly (e.g. right file, but
the line shows only part of the claim); n = they do not support it;
s = cannot judge. You can stop at any time (Ctrl+C) and run the command again
later: answered items are skipped.
"""
import csv
import json
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIRST = ROOT / "execution" / "results" / "A"
RERUN = ROOT / "execution-rerun" / "results" / "A"
SOURCES = {"payin-processor": RERUN, "agents-commissions": RERUN, "credit-card-processor": FIRST, "bank-interface": FIRST, "payout-processor": FIRST}
OUT = Path(__file__).parent / "results" / "check1-citations.csv"
SEED, PER_SERVICE, CONTEXT, MAX_LINES = 2026, 20, 3, 40
SECTIONS = [("q3_endpoints", "endpoint", "Q3 operation exposed"), ("q4_sync_calls", "endpoint", "Q4 outgoing call"),
            ("q5_topics_published", "topic", "Q5 topic published"), ("q6_topics_consumed", "topic", "Q6 topic consumed"),
            ("q7_data_sources", "name", "Q7 data source"), ("q8_deployment_dependencies", "service", "Q8 deployment dependency"),
            ("q9_module_components", "service", "Q9 module component")]
REF = re.compile(r"^(repos/.+?)(?::(\d+)(?:-(\d+))?)?$")


def items(service):
    data = json.load(open(SOURCES[service] / f"{service}.json", encoding="utf-8"))
    out = []
    for key, field, label in SECTIONS:
        for e in data.get(key, []):
            refs = [r for r in e.get("evidence", []) if r.startswith("repos/")]
            if refs:
                extra = e.get("provider") or ""
                out.append({"service": service, "question": label,
                            "item": (f"{extra}: " if extra else "") + str(e.get(field, "")),
                            "ref": refs[0], "notes": e.get("notes") or e.get("why") or e.get("what_it_does") or ""})
    return out


def sample():
    chosen = []
    for s in SOURCES:
        pool = items(s)
        rng = random.Random(f"{SEED}-{s}")
        chosen += rng.sample(pool, min(PER_SERVICE, len(pool)))
    return chosen


def show(ws, ref):
    m = REF.match(ref)
    path = ws / m.group(1)
    if not path.is_file():
        print(f"   !! file not found in the snapshot: {m.group(1)}")
        return
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    if not m.group(2):
        print(f"   (whole file cited: {len(lines)} lines; first lines shown)")
        lo, hi, a, b = 1, min(len(lines), 15), 0, 0
    else:
        a = int(m.group(2)); b = int(m.group(3) or a)
        lo, hi = max(1, a - CONTEXT), min(len(lines), b + CONTEXT)
        hi = min(hi, lo + MAX_LINES - 1)
    for i in range(lo, hi + 1):
        mark = ">>" if a <= i <= b else "  "
        print(f"   {mark}{i:5d} | {lines[i - 1][:160]}")


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    ws = Path(sys.argv[1]).expanduser()
    if not (ws / "repos").is_dir():
        sys.exit(f"{ws}/repos not found: rebuild the snapshot first (see experiment/checks/README.md)")
    OUT.parent.mkdir(exist_ok=True)
    done = {}
    if OUT.exists():
        for r in csv.DictReader(open(OUT, encoding="utf-8")):
            done[(r["service"], r["question"], r["item"], r["ref"])] = r
    todo = sample()
    new = not OUT.exists()
    with open(OUT, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["service", "question", "item", "ref", "verdict", "note"])
        if new:
            w.writeheader()
        for n, it in enumerate(todo, 1):
            key = (it["service"], it["question"], it["item"], it["ref"])
            if key in done:
                continue
            print("\n" + "=" * 100)
            print(f"[{n}/{len(todo)}] {it['service']} | {it['question']}")
            print(f"   ITEM : {it['item']}")
            if it["notes"]:
                print(f"   NOTES: {it['notes'][:300]}")
            print(f"   CITED: {it['ref']}\n")
            show(ws, it["ref"])
            v = ""
            while v not in ("y", "p", "n", "s"):
                v = input("\n   Do these lines support the item? [y]es / [p]artly / [n]o / [s]kip: ").strip().lower()
            note = input("   Note (optional, Enter to skip): ").strip()
            w.writerow({**{k: it[k] for k in ("service", "question", "item", "ref")}, "verdict": v, "note": note})
            f.flush()
    rows = list(csv.DictReader(open(OUT, encoding="utf-8")))
    print(f"\nDone: {len(rows)} items checked. Results: {OUT}")
    for s in SOURCES:
        vs = [r["verdict"] for r in rows if r["service"] == s]
        print(f"  {s:14} y={vs.count('y'):2} p={vs.count('p'):2} n={vs.count('n'):2} s={vs.count('s'):2}")


if __name__ == "__main__":
    main()
