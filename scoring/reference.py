"""Parse the reconciled characterization (execution-b/B0-inputs/characterization)
into per-service reference sets used to score Task A."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHAR = ROOT / "execution-b" / "B0-inputs" / "characterization"
IN_SCOPE = {"payin-processor": "payin-processor", "payout-processor": "payout-processor", "agents-commissions": "agents-commissions",
            "bank-interface": "bank-interface", "credit-card-processor": "credit-card-processor"}


def _matrix(name):
    rows = list(csv.reader(open(CHAR / name, encoding="utf-8")))
    header = rows[1]
    cols = {i: h.strip() for i, h in enumerate(header) if i >= 2 and h.strip()}
    cells = {}
    for r in rows[2:]:
        if len(r) < 2 or not r[1].strip():
            continue
        sender = r[1].strip()
        for i, h in cols.items():
            v = r[i].strip() if i < len(r) else ""
            if v:
                cells[(sender, h)] = v
    return cells


def _num(v):
    return int(v.split()[0])


def sync():
    """{service: {"size": n, "calls": {receiver: n}, "callers": {sender: n}}}"""
    cells = _matrix("sync.csv")
    out = {}
    for raw, sid in IN_SCOPE.items():
        calls = {r: _num(v) for (s, r), v in cells.items() if s == raw and r != raw and not r.startswith(("Depends", "Important"))}
        callers = {s: _num(v) for (s, r), v in cells.items() if r == raw and s != raw and not s.startswith(("Depends", "Important"))}
        out[sid] = {"size": _num(cells[(raw, raw)]) if (raw, raw) in cells else None, "calls": calls, "callers": callers}
    return out


def async_():
    """{service: {"published": n, "subscribers": {sub: n}, "publishers": {pub: n}}}"""
    cells = _matrix("async.csv")
    out = {}
    for raw, sid in IN_SCOPE.items():
        subs = {r: _num(v) for (s, r), v in cells.items() if s == raw and r != raw and not r.startswith(("Depends", "Important"))}
        pubs = {s: _num(v) for (s, r), v in cells.items() if r == raw and s != raw and not s.startswith(("Depends", "Important"))}
        out[sid] = {"published": _num(cells[(raw, raw)]) if (raw, raw) in cells else None, "subscribers": subs, "publishers": pubs}
    return out


def databases():
    rows = list(csv.reader(open(CHAR / "databases.csv", encoding="utf-8")))
    services = rows[1]
    out = {sid: {} for sid in IN_SCOPE.values()}
    for r in rows[2:]:
        ds = r[1].strip()
        for i in range(2, 7):
            if r[i].strip():
                out[IN_SCOPE[services[i].strip()]][ds] = r[i].strip()
    return out


if __name__ == "__main__":
    s, a, d = sync(), async_(), databases()
    for sid in IN_SCOPE.values():
        print(sid, "size", s[sid]["size"], "| calls", s[sid]["calls"], "| callers", s[sid]["callers"])
        print("   async published", a[sid]["published"], "| subs", a[sid]["subscribers"], "| pubs", a[sid]["publishers"])
        print("   db", d[sid])
