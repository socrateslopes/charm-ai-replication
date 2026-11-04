"""Micro-averaged Task A metrics across the five services (from score_a.py output)."""
import collections
import csv
from pathlib import Path

import sys  # noqa: E402
OUT = Path(__file__).parent / "results" / ("first-execution" if "--first-execution" in sys.argv else "")
rows = list(csv.DictReader(open(OUT / "taskA-pairs.csv")))
print("Pair level against the reconciled characterization (micro-averaged):")
agg = collections.defaultdict(lambda: [0, 0, 0, 0, 0])
for r in rows:
    n = int(r["n_reconciled"])
    cnt = lambda k: len([x for x in r[k].split("; ") if x])
    a = agg[r["dimension"]]
    a[0] += n; a[1] += n - cnt("agent_missed"); a[2] += cnt("agent_extra"); a[3] += n - cnt("dev_missed"); a[4] += cnt("dev_extra")
    if r["dev_f1"] not in ("1.00", ""):
        print("   developer differs from reconciled:", r["service"], r["dimension"], r["dev_missed"], "|", r["dev_extra"])
for d, (n, atp, afp, dtp, dfp) in agg.items():
    print(f"  {d:22} n={n:3} agent R={atp/n:.2f} P={atp/(atp+afp):.2f} (extra {afp:2}) | developers R={dtp/n:.2f} P={dtp/(dtp+dfp):.2f}")
tot = [sum(v[i] for v in agg.values()) for i in range(5)]
print(f"  {'all':22} n={tot[0]:3} agent R={tot[1]/tot[0]:.2f} P={tot[1]/(tot[1]+tot[2]):.2f} | developers R={tot[3]/tot[0]:.2f} P={tot[3]/(tot[3]+tot[4]):.2f}")

print("\nItem level against the questionnaires (micro-averaged):")
items = list(csv.DictReader(open(OUT / "taskA-items.csv")))
agg = collections.defaultdict(lambda: [0, 0, 0])
for r in items:
    if r["precision"]:
        a = agg[r["dimension"]]; a[0] += int(r["n_reference"]); a[1] += int(r["n_agent"]); a[2] += int(r["tp_or_active"])
for d, (nr, na, tp) in agg.items():
    p, rr = tp / na, tp / nr
    print(f"  {d:20} questionnaire={nr:3} agent={na:3} matched={tp:3} P={p:.2f} R={rr:.2f} F1={2*p*rr/(p+rr):.2f}")

# ---- error taxonomy of the items that differ from the questionnaires (rules
# first, researcher-checked; protocol Section 9.1 "Error taxonomy")
import re  # noqa: E402
# Generic subset of the rules; the case-specific ones (names from the
# company's code) are not public.
# Each rule is (category, regex on "question,kind,item"); first match wins.
TAXONOMY = [
    ("possibly unused, legacy or test", r"possibly unused|/test/|/maintenance/"),
    ("platform or infrastructure", r"/health|/metrics|swagger|actuator|cdc|exporter|monitoring"),
    ("granularity or boundary", r"triggers|-scheduler$"),
    ("naming or method mismatch", r"(?!)"),
]
diffs = list(csv.DictReader(open(OUT / "taskA-item-diffs.csv")))
cats = collections.Counter()
for d in diffs:
    line = f"{d['question']},{d['kind']},{d['item']}".lower()
    cat = next((c for c, pat in TAXONOMY if re.search(pat, line)), "other: not in the questionnaire")
    d["category"] = cat
    cats[(d["kind"].split()[0], cat)] += 1
with open(OUT / "taskA-item-diffs-classified.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["service", "question", "kind", "item", "category"])
    w.writeheader(); w.writerows(diffs)
print("\nItems that differ from the questionnaires, by category:")
for (kind, cat), n in sorted(cats.items()):
    print(f"  {kind:6} {cat:35} {n}")
