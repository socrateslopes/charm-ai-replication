#!/usr/bin/env python3
"""Spot-check of check 2: does a person agree with Claude's drawback verdicts?

Check 2 (is each drawback stated in Brown, Woolf and Yoder?) was judged by
Claude. This script draws a fixed random sample of 15 of the 59 verdicts
(5 yes, 5 partly, 5 no), shows each drawback with Claude's verdict, section and
note, and records whether you agree. Keep the book open at the section shown.

Usage (from the root of the jise repository):
    python3 experiment/checks/spot_check_drawbacks.py

Answers: a = agree; d = disagree (you then give your own verdict: yes, partly
or no); s = skip. Stop at any time with Ctrl+C and run it again later:
answered rows are skipped. Results go to
experiment/checks/results/check2-spotcheck.csv.
"""
import csv
import random
from pathlib import Path

HERE = Path(__file__).parent
SRC = HERE / "check2-drawbacks.csv"
OUT = HERE / "results" / "check2-spotcheck.csv"
SEED, PER_VERDICT = "2026-spotcheck", 5


def sample():
    rows = list(csv.DictReader(open(SRC, encoding="utf-8")))
    rng = random.Random(SEED)
    chosen = []
    for v in ("yes", "partly", "no"):
        pool = [r for r in rows if r["documented"] == v]
        chosen += rng.sample(pool, min(PER_VERDICT, len(pool)))
    rng.shuffle(chosen)
    return chosen


def main():
    OUT.parent.mkdir(exist_ok=True)
    done = set()
    if OUT.exists():
        done = {r["drawback_id"] for r in csv.DictReader(open(OUT, encoding="utf-8"))}
    todo = sample()
    new = not OUT.exists()
    with open(OUT, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["drawback_id", "pattern", "claude_verdict", "answer", "your_verdict", "note"])
        if new:
            w.writeheader()
        for n, r in enumerate(todo, 1):
            if r["drawback_id"] in done:
                continue
            print("\n" + "=" * 100)
            print(f"[{n}/{len(todo)}] {r['drawback_id']} | {r['pattern']} ({r['chapter']})")
            print(f"   DRAWBACK : {r['drawback']}")
            print(f"   CLAUDE   : {r['documented'].upper()}")
            print(f"   WHERE    : {r['where'] or '(no section: not found in the book)'}")
            print(f"   NOTE     : {r['note']}")
            a = ""
            while a not in ("a", "d", "s"):
                a = input("\n   Do you agree? [a]gree / [d]isagree / [s]kip: ").strip().lower()
            yours = r["documented"] if a == "a" else ""
            if a == "d":
                while yours not in ("yes", "partly", "no"):
                    yours = input("   Your verdict [yes / partly / no]: ").strip().lower()
            note = input("   Note (optional, Enter to skip): ").strip()
            w.writerow({"drawback_id": r["drawback_id"], "pattern": r["pattern"], "claude_verdict": r["documented"],
                        "answer": {"a": "agree", "d": "disagree", "s": "skip"}[a], "your_verdict": yours, "note": note})
            f.flush()
    rows = list(csv.DictReader(open(OUT, encoding="utf-8")))
    ans = [r["answer"] for r in rows]
    print(f"\nDone: {len(rows)} rows. Agree {ans.count('agree')}, disagree {ans.count('disagree')}, skip {ans.count('skip')}.")
    print(f"Results: {OUT}")


if __name__ == "__main__":
    main()
