#!/usr/bin/env python3
"""Score Tasks B0 and B1 (protocol Section 9.2).

Answer keys: patterns identified and suggested by participants, and the three
flaw categories. The pattern counts are those of the revised dissertation
(transcript re-check of 2026-10-30; protocol Section 11, deviation 12). The
pre-registered counts (spreadsheet tabs "reviewed of Patterns Identified",
column Actual, and "Copy of Patterns Suggestion") are kept as *_PREREGISTERED
and used with --preregistered-key. Issue-to-category matching is the
researcher's adjudication (ISSUE_MATCH).
Writes experiment/scoring/results/taskB-*.csv (results/preregistered-key/ with
--preregistered-key).
"""
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / "execution" / "results"
RERUN = ROOT / "execution-rerun" / "results"     # B1 repeated (protocol Section 11, deviation 4)
FIRST = "--first-execution" in sys.argv
ISSUE_MATCH = None  # set in main()
B0IN = ROOT / "execution-b" / "B0-inputs"
B1IN = ROOT / ("execution-b" if "--first-execution" in __import__("sys").argv else "execution-rerun-b") / "B1-inputs" / "developer-input"
PREREG = "--preregistered-key" in sys.argv
OUT = Path(__file__).parent / "results" / ("first-execution" if FIRST else "") / ("preregistered-key" if PREREG else "")

PRESENT_PREREGISTERED = {"Domain Microservice": 7, "Event Notifier": 5, "Self-Managed Data Store": 3, "Event Choreography": 3,
           "Dispatcher": 3, "Polyglot Development": 3, "Anti-Corruption Layer": 3, "Reactive Component": 3,
           "Adapter Microservice": 2, "Model Around the Domain": 2, "Event Sourcing": 2, "Event": 2,
           "Ubiquitous Language": 1, "Repositories": 1}
SUGGESTED_PREREGISTERED = {"Domain Microservice": 5, "Reactive Component": 5, "Event Choreography": 4, "Event": 3,
             "Event API": 2, "Anti-Corruption Layer": 2, "Event Notifier": 2, "Bounded Context": 2,
             "Service Orchestrator": 1}
# Revised key (dissertation, Figures 5.1 and 5.2): Repositories +1 (P5), Event
# Backbone identified and suggested (P1), Event Notifier suggested by 3.
PRESENT_REVISED = {**PRESENT_PREREGISTERED, "Repositories": 2, "Event Backbone": 1}
SUGGESTED_REVISED = {**SUGGESTED_PREREGISTERED, "Event Notifier": 3, "Event Backbone": 1}
PRESENT = PRESENT_PREREGISTERED if "--preregistered-key" in sys.argv else PRESENT_REVISED
SUGGESTED = SUGGESTED_PREREGISTERED if "--preregistered-key" in sys.argv else SUGGESTED_REVISED
NOT_IN_CATALOG = {"Ubiquitous Language"}
# Researcher adjudication: issue id -> flaw categories it matches (same service
# and same mechanism). 1 = synchronous coupling / single point of failure on a
# third party; 2 = hub with high afferent coupling (agents-commissions); 3 = oversized
# services with blurred domain boundaries.
ISSUE_MATCH_FIRST = {"B0": {"I1": [1, 3], "I3": [3], "I5": [2]},
                     "B1": {"I1": [3], "I2": [1], "I7": [3], "I12": [2]}}
# B1 rerun (execution-rerun/results/B1): I6 is matched to category 2 on the
# same grounds as I12 of the first B1 run (agents-commissions's API bound to many clients).
ISSUE_MATCH_RERUN = {"B0": ISSUE_MATCH_FIRST["B0"],
                     "B1": {"I1": [3], "I2": [1], "I5": [3], "I6": [2], "I9": [3]}}


def norm(p):
    return re.sub(r"\s*\(.*\)", "", p).strip()


def valid_refs():
    sync = list(csv.reader(open(B0IN / "characterization" / "sync.csv", encoding="utf-8")))
    asy = list(csv.reader(open(B0IN / "characterization" / "async.csv", encoding="utf-8")))

    def cells(rows):
        hdr = rows[1]
        out = set()
        for r in rows[2:]:
            for i, v in enumerate(r):
                if i >= 2 and v.strip() and i < len(hdr) and hdr[i].strip():
                    out.add((r[1].strip(), hdr[i].strip()))
        return out
    db = {r[1].strip() for r in csv.reader(open(B0IN / "characterization" / "databases.csv", encoding="utf-8")) if len(r) > 1}
    svc = set(re.findall(r"^#+\s*(.+?)\s*$", (B0IN / "services.md").read_text(encoding="utf-8"), re.M))
    qc = set(re.findall(r"^#+\s*(.+?)\s*$", (B1IN / "questionnaire-comments.md").read_text(encoding="utf-8"), re.M))
    ts = {}
    for f in (B1IN / "interviews").glob("P*.md"):
        ts[f.stem] = re.findall(r"^### (\d\d:\d\d:\d\d)", f.read_text(encoding="utf-8"), re.M)
    return cells(sync), cells(asy), db, {s.lower() for s in svc}, {s.lower() for s in qc}, ts


def check_ref(ref, V):
    sync, asy, db, svc, qc, ts = V
    m = re.match(r"^(SYNC|ASYNC)\[(.+?)->(.+?)\]$", ref)
    if m:
        return (m.group(2), m.group(3)) in (sync if m.group(1) == "SYNC" else asy)
    m = re.match(r"^DB\[(.+)\]$", ref)
    if m:
        return m.group(1) in db
    m = re.match(r"^SVC\[(.+)\]$", ref)
    if m:
        return any(m.group(1).lower() in s for s in svc)
    m = re.match(r"^Q\[(.+)\]$", ref)
    if m:
        return any(m.group(1).lower() in s for s in qc)
    m = re.match(r"^(P\d)@(\d\d:\d\d:\d\d)$", ref)
    if m:
        return m.group(2) in ts.get(m.group(1), [])
    return ref == "CTX"


def main():
    global ISSUE_MATCH
    ISSUE_MATCH = ISSUE_MATCH_FIRST if FIRST else ISSUE_MATCH_RERUN
    OUT.mkdir(parents=True, exist_ok=True)
    V = valid_refs()
    nP, nC = len(PRESENT), len(set(PRESENT) - NOT_IN_CATALOG)
    nS, nS2 = len(SUGGESTED), sum(1 for v in SUGGESTED.values() if v >= 2)
    rows, extra_rows = [], []
    for c in ("B0", "B1"):
        base = RERUN if c == "B1" and not FIRST else RES
        d = json.load(open(base / c / "assessment.json", encoding="utf-8"))
        present = {norm(e["pattern"]) for e in d["patterns_present"]}
        tp = present & set(PRESENT)
        rec = [norm(e["pattern"]) for e in d["recommendations"]]
        rtp = set(rec) & set(SUGGESTED)
        cats = {k for v in ISSUE_MATCH[c].values() for k in v}
        claims = [e for s in ("patterns_present", "issues", "recommendations") for e in d[s]]
        refs = [r for e in claims for r in e.get("evidence", [])]
        bad = sorted({r for r in refs if not check_ref(r, V)})
        ok_claims = sum(1 for e in claims if e.get("evidence") and all(check_ref(r, V) for r in e["evidence"]))
        rows += [
            (c, "patterns present: precision", f"{len(tp)}/{len(present)}", len(tp) / len(present)),
            (c, f"patterns present: recall ({nP})", f"{len(tp)}/{nP}", len(tp) / nP),
            (c, f"patterns present: recall, catalog only ({nC})", f"{len(tp)}/{nC}", len(tp) / nC),
            (c, "patterns present: recall weighted by participants",
             f"{sum(PRESENT[p] for p in tp)}/{sum(PRESENT.values())}", sum(PRESENT[p] for p in tp) / sum(PRESENT.values())),
            (c, f"recommended: recall ({nS})", f"{len(rtp)}/{nS}", len(rtp) / nS),
            (c, f"recommended: recall, >=2 participants ({nS2})", f"{len({p for p in rtp if SUGGESTED[p] >= 2})}/{nS2}",
             len({p for p in rtp if SUGGESTED[p] >= 2}) / nS2),
            (c, "recommended: recall weighted by participants",
             f"{sum(SUGGESTED[p] for p in rtp)}/{sum(SUGGESTED.values())}", sum(SUGGESTED[p] for p in rtp) / sum(SUGGESTED.values())),
            (c, "recommended: precision", f"{len(rtp)}/{len(set(rec))}", len(rtp) / len(set(rec))),
            (c, "flaw categories recalled (3)", f"{len(cats)}/3", len(cats) / 3),
            (c, "issues matching a category", f"{len(ISSUE_MATCH[c])}/{len(d['issues'])}", len(ISSUE_MATCH[c]) / len(d["issues"])),
            (c, "claims with all evidence valid", f"{ok_claims}/{len(claims)}", ok_claims / len(claims)),
            (c, "evidence references valid", f"{len(refs) - sum(refs.count(b) for b in bad)}/{len(refs)}",
             (len(refs) - sum(refs.count(b) for b in bad)) / len(refs)),
        ]
        for p in sorted(present - set(PRESENT)):
            extra_rows.append((c, "present, not in answer key", p))
        for p in sorted(set(PRESENT) - present):
            extra_rows.append((c, "present in answer key, not found", p))
        for p in [p for p in rec if p not in SUGGESTED]:
            extra_rows.append((c, "recommended, not suggested by participants", p))
        for p in sorted(set(SUGGESTED) - set(rec)):
            extra_rows.append((c, "suggested by participants, not recommended", p))
        for b in bad:
            extra_rows.append((c, "invalid evidence reference", b))
    with open(OUT / "taskB-metrics.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["condition", "metric", "count", "value"])
        w.writerows([(a, b, cnt, f"{v:.2f}") for a, b, cnt, v in rows])
    with open(OUT / "taskB-differences.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["condition", "kind", "item"])
        w.writerows(extra_rows)
    for a, b, cnt, v in rows:
        print(f"{a}  {b:50} {cnt:>8}  {v:.2f}")
    print()
    for r in extra_rows:
        print("  ".join(r))


if __name__ == "__main__":
    main()
