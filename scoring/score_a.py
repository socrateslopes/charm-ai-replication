#!/usr/bin/env python3
"""Score Task A (protocol Section 9.1).

Item level: agent output (execution/results/A/<service>.json) against the
developers' questionnaire (questionnaires.py). Pair level: agent output and
questionnaire against the reconciled characterization (reference.py).

Normalization and aliases are defined in this file (the "alias table" of
the protocol). Writes experiment/scoring/results/taskA-*.csv and prints a
summary. Usage: python3 experiment/scoring/score_a.py [--verbose]
"""
import csv
import json
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import questionnaires as Q  # noqa: E402
import reference as R  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "execution" / "results" / "A"
# Runs repeated in execution-rerun/ (protocol Section 11, deviation 1) replace
# the first-execution runs unless --first-execution is given.
RERUN = ROOT / "execution-rerun" / "results" / "A"
RERUN_SERVICES = {"payin-processor", "agents-commissions"}
FIRST = "--first-execution" in sys.argv
OUT = Path(__file__).parent / "results" / ("first-execution" if FIRST else "")


def rdir(service):
    return RERUN if service in RERUN_SERVICES and not FIRST else RESULTS
SERVICES = ["payin-processor", "credit-card-processor", "agents-commissions", "bank-interface", "payout-processor"]
VERBOSE = "--verbose" in sys.argv

# ---------------------------------------------------------------- endpoints
# Case-specific table (not public: it holds names from the company's code and
# internal services). Same structure as in the private analysis; empty here.
# Base paths of third-party APIs, removed so that the same operation written with
# a configured base URL or a full URL compares equal (regexes).
BASE_PREFIXES = []
# Same operation, different spelling (researcher-adjudicated).
PATH_ALIASES = {}
METHODS = r"GET|POST|PUT|PATCH|DELETE"


def ep_key(s):
    s = s.replace("\\", "").replace("[", "{").strip()
    m = re.match(rf"^({METHODS})\s+(\S+)", s, re.I)
    method, path = (m.group(1).upper(), m.group(2)) if m else (None, s.split()[0] if s.split() else s)
    path = path.split("?")[0]
    path = re.sub(r"^https?://[^/]+", "", path)
    path = re.sub(r"^\{[^}/]*\}", "", path)          # {service.baseUrl}/...
    path = re.sub(r"\{[^}]*\}|:[\w-]+|\$\w+", "{}", path)
    path = "/" + path.strip("/").lower()
    for p in BASE_PREFIXES:
        path = re.sub("^" + p + r"(?=/|$)", "", path) or "/"
    return method, PATH_ALIASES.get(path, path)


def match(ref_items, agent_items, same):
    """Greedy one-to-one matching. Returns list of (ref_idx, agent_idx)."""
    pairs, used = [], set()
    for i, r in enumerate(ref_items):
        for j, a in enumerate(agent_items):
            if j not in used and same(r, a):
                pairs.append((i, j))
                used.add(j)
                break
    return pairs


def ep_same(r, a):
    (rm, rp), (am, ap) = r, a
    return rp == ap and (rm is None or am is None or rm == am)


def dedupe(keys):
    seen, out = set(), []
    for k in keys:
        if k not in seen:
            seen.add(k)
            out.append(k)
    return out


# ------------------------------------------------------------------- topics
# Case-specific table (not public: it holds names from the company's code and
# internal services). Same structure as in the private analysis; empty here.
TOPIC_ALIASES = {}
SNAKE = re.compile(r"\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+\b")


# Researcher-adjudicated expansions: queues whose label carries no message
# types, but whose message types the agent lists in the item's own notes.
# Case-specific table (not public: it holds names from the company's code and
# internal services). Same structure as in the private analysis; empty here.
TOPIC_EXPANSIONS = {}  # {(service, queue key): [message types]}

def topic_keys_item(item, service):
    keys = topic_keys(item["topic"], service)
    exp = TOPIC_EXPANSIONS.get((service, keys[0])) if len(keys) == 1 else None
    if exp and all(t in item.get("notes", "") for t in exp):
        return exp
    return keys


def topic_keys(label, service):
    """Event-type names (UPPER_SNAKE) when the label carries them, else the
    normalized queue/topic name."""
    tokens = SNAKE.findall(label)
    if tokens:
        return dedupe(tokens)
    s = label.split("(")[0].strip()
    s = re.sub(r"^(sqs|sns|kafka)\s*:?\s*", "", s, flags=re.I).replace("<env>", "")
    s = re.sub(r"[^a-z0-9]", "", s.lower())
    s = re.sub(r"^prod", "", s)
    s = re.sub("^" + service.replace("-", ""), "", s) if service == "credit-card-processor" else s
    return [TOPIC_ALIASES.get(s, s)]


# ------------------------------------------------------------ counterparts
# Canonical names of counterpart services, matched in order on the lowercased
# label (first match wins). None = ignored (infrastructure, not a service).
# Checked on the whole label first: schedulers that the reconciled table names
# as separate publishers even when the agent calls them module components.
# Case-specific table (not public: it holds names from the company's code and
# internal services). Same structure as in the private analysis; empty here.
PRIORITY = []  # [(regex on the whole label, canonical name)]
CANON = []  # [(regex on the label head, canonical name or None)], first match wins
# Per-service aliases (researcher-adjudicated).
# Case-specific table (not public: it holds names from the company's code and
# internal services). Same structure as in the private analysis; empty here.
SERVICE_CANON = {}  # {service: [(regex, canonical name)]}
SELF = {"payin-processor": "payin-processor", "credit-card-processor": "credit-card-processor", "agents-commissions": "agents-commissions",
        "bank-interface": "bank-interface", "payout-processor": "payout-processor"}


def canon(name, service):
    """Canonical counterpart name. The label's head (text before any
    parenthesis) is used, so "<service> (<service>-job)" is the service itself."""
    full = name.strip().lower()
    for pat, c in PRIORITY:
        if re.search(pat, full):
            return c
    n = full.split("(")[0].strip() or full
    own = SELF[service].split()[0]
    if re.match(rf"{own}[- ]", n):            # own module component, kept as written
        return n
    for pat, c in SERVICE_CANON.get(service, []) + CANON:
        m = re.search(pat, n)
        if m:
            return c(m) if callable(c) else c
    return n


def is_own(c, service):
    """Own module components and the service itself (excluded from pairs)."""
    own = SELF[service]
    first = own.split()[0]
    return c is None or c == own or c.startswith(first + "-") or c.startswith(first + " ")


# ------------------------------------------------------------ data sources
# Case-specific table (not public: it holds names from the company's code and
# internal services). Same structure as in the private analysis; empty here.
DS_ALIASES = {s: [] for s in SERVICES}  # {service: [(regex, data source name)]}

def ds_canon(name, service):
    n = name.strip().lower()
    for pat, c in DS_ALIASES[service]:
        if re.search(pat, n):
            return c
    return "extra:" + n[:50]


# ------------------------------------------------------------------ metrics
def prf(tp, n_ref, n_agent):
    p = tp / n_agent if n_agent else None
    r = tp / n_ref if n_ref else None
    f = 2 * p * r / (p + r) if p and r else (0.0 if p is not None and r is not None else None)
    return p, r, f


def fmt(x):
    return "" if x is None else f"{x:.2f}"


def set_prf(ref, agent):
    ref, agent = set(ref), set(agent)
    return prf(len(ref & agent), len(ref), len(agent)), sorted(ref - agent), sorted(agent - ref)


def minutes(log):
    times = re.findall(r"(\w{3} \w{3}\s+\d+ \d\d:\d\d:\d\d) -03 2026|(2026-\d\d-\d\d \d\d:\d\d:\d\d) -0300", log)
    stamps = []
    for a, b in times[:2]:
        stamps.append(datetime.strptime(a.split()[-1] if a else b.split()[-1], "%H:%M:%S"))
    return round((stamps[1] - stamps[0]).seconds / 60) if len(stamps) == 2 else None


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    sync, asy, dbs = R.sync(), R.async_(), R.databases()
    item_rows, pair_rows, detail, count_rows = [], [], [], []
    for s in SERVICES:
        a = json.load(open(rdir(s) / f"{s}.json", encoding="utf-8"))
        q = Q.ALL[s]
        log = (rdir(s) / f"{s}.log.md").read_text(encoding="utf-8")

        # ---- item level: Q3 endpoints
        ref = dedupe(ep_key(e) for e, _ in q["q3"])
        ag_all = [(ep_key(e["endpoint"]), e) for e in a["q3_endpoints"]]
        ag = dedupe(k for k, _ in ag_all)
        m = match(ref, ag, ep_same)
        item_rows.append((s, "Q3 endpoints", len(ref), len(ag), len(m), *prf(len(m), len(ref), len(ag))))
        unused = {k for k, e in ag_all if e.get("possibly_unused")}
        matched_ag = {ag[j] for _, j in m}
        detail += [(s, "Q3", "missed", f"{ref[i][0] or ''} {ref[i][1]}") for i in range(len(ref)) if i not in {x for x, _ in m}]
        detail += [(s, "Q3", "extra" + (" (possibly unused)" if k in unused else ""), f"{k[0] or ''} {k[1]}")
                   for k in ag if k not in matched_ag]

        # ---- item level: Q4 sync calls (provider + endpoint)
        ref4 = dedupe((canon(p, s), ep_key(e)) for e, p in q["q4"])
        ag4 = dedupe((canon(e["provider"], s), ep_key(e["endpoint"])) for e in a["q4_sync_calls"])
        m4 = match(ref4, ag4, lambda r, x: r[0] == x[0] and ep_same(r[1], x[1]))
        item_rows.append((s, "Q4 sync calls", len(ref4), len(ag4), len(m4), *prf(len(m4), len(ref4), len(ag4))))
        mi = {i for i, _ in m4}
        mj = {j for _, j in m4}
        detail += [(s, "Q4", "missed", f"{r[0]}: {r[1][0] or ''} {r[1][1]}") for i, r in enumerate(ref4) if i not in mi]
        detail += [(s, "Q4", "extra", f"{x[0]}: {x[1][0] or ''} {x[1][1]}") for j, x in enumerate(ag4) if j not in mj]

        # ---- item level: Q5 / Q6 topics
        for qn, key in (("q5", "q5_topics_published"), ("q6", "q6_topics_consumed")):
            refk = dedupe(k for t, _ in q[qn] for k in topic_keys(t, s))
            agk = dedupe(k for e in a[key] for k in topic_keys_item(e, s))
            tp = len(set(refk) & set(agk))
            item_rows.append((s, f"{qn.upper()} topics", len(refk), len(agk), tp, *prf(tp, len(refk), len(agk))))
            detail += [(s, qn.upper(), "missed", k) for k in refk if k not in agk]
            detail += [(s, qn.upper(), "extra", k) for k in agk if k not in refk]

        # ---- topics combined (direction, key), as in Table taskA
        refT = {(qn, k) for qn in ("q5", "q6") for t, _ in q[qn] for k in topic_keys(t, s)}
        agT = {(qn, k) for qn, key in (("q5", "q5_topics_published"), ("q6", "q6_topics_consumed"))
               for e in a[key] for k in topic_keys_item(e, s)}
        tp = len(refT & agT)
        item_rows.append((s, "Topics (Q5+Q6)", len(refT), len(agT), tp, *prf(tp, len(refT), len(agT))))

        # ---- operation counts per provider against the reconciled table
        per_prov = {}
        for prov, key in ag4:
            per_prov.setdefault(prov, set()).add(key)
        for prov, n in sync[s]["calls"].items():
            c = canon(prov, s)
            count_rows.append((s, c, n, len({k for k in per_prov.get(c, set())}),
                               len({ep for p, ep in ref4 if p == c})))

        # ---- item level: Q7 data sources (name), action agreement
        refd = {ds_canon(n, s): act for n, _, _, act, _ in q["q7"]}
        agd = {ds_canon(e["name"], s): e["actions"] for e in a["q7_data_sources"]}
        tp = len(set(refd) & set(agd))
        item_rows.append((s, "Q7 data sources", len(refd), len(agd), tp, *prf(tp, len(refd), len(agd))))
        detail += [(s, "Q7", "missed", k) for k in refd if k not in agd]
        detail += [(s, "Q7", "extra", k) for k in agd if k not in refd]

        # ---- item level: Q9 module components (names, loose)
        ref9 = [c.lower() for c in q["q9"]]
        ag9 = [c["service"].lower() for c in a["q9_module_components"]]
        own = s.split("-")[0]
        def comp(c):
            c = re.sub(r"\(.*", "", c).strip().replace(" ", "-")
            c = re.sub(r"-job$", "", c)
            c = re.sub(r"-(api|receipts?)$", lambda x: "-receipt" if "receipt" in x.group(0) else "", c)
            return c
        ref9c = {comp(c) for c in ref9 if comp(c) not in (own, s)}
        ag9c = {comp(c) for c in ag9 if comp(c) not in (own, s)}
        tp = len(ref9c & ag9c)
        item_rows.append((s, "Q9 components", len(ref9c), len(ag9c), tp, *prf(tp, len(ref9c), len(ag9c))))
        detail += [(s, "Q9", "missed", k) for k in sorted(ref9c - ag9c)]
        detail += [(s, "Q9", "extra", k) for k in sorted(ag9c - ref9c)]

        # ---- pair level against the reconciled characterization
        def others(names):
            return {c for c in (canon(n, s) for n in names) if not is_own(c, s)}
        rs, ra = sync[s], asy[s]
        ref_pairs = {
            "sync: depends on": {c for c in (canon(n, s) for n in rs["calls"]) if not is_own(c, s)},
            "sync: invoked by": {c for c in (canon(n, s) for n in rs["callers"]) if not is_own(c, s)},
            "async: consumed by": {c for c in (canon(n, s) for n in ra["subscribers"]) if not is_own(c, s)},
            "async: consumes from": {c for c in (canon(n, s) for n in ra["publishers"]) if not is_own(c, s)},
            "data sources": set(dbs[s]),
        }
        dev_pairs = {
            "sync: depends on": others(p for _, p in q["q4"]),
            "sync: invoked by": others(c for _, cs in q["q3"] for c in cs),
            "async: consumed by": others(c for _, cs in q["q5"] for c in cs),
            "async: consumes from": others(c for _, cs in q["q6"] for c in cs),
            "data sources": {ds_canon(n, s) for n, *_ in q["q7"]},
        }
        agent_pairs = {
            "sync: depends on": others(e["provider"] for e in a["q4_sync_calls"]),
            "sync: invoked by": others(c["service"] for e in a["q3_endpoints"] for c in e.get("consumed_by", [])),
            "async: consumed by": others(c["service"] for e in a["q5_topics_published"] for c in e.get("consumed_by", [])),
            "async: consumes from": others(c["service"] for e in a["q6_topics_consumed"] for c in e.get("produced_by", [])),
            "data sources": {ds_canon(e["name"], s) for e in a["q7_data_sources"]},
        }
        for dim in ref_pairs:
            (ap, ar, af), amiss, aextra = set_prf(ref_pairs[dim], agent_pairs[dim])
            (dp, dr, df), dmiss, dextra = set_prf(ref_pairs[dim], dev_pairs[dim])
            pair_rows.append((s, dim, len(ref_pairs[dim]), ap, ar, af, dp, dr, df,
                              "; ".join(amiss), "; ".join(aextra), "; ".join(dmiss), "; ".join(dextra)))

        # ---- size and time
        n_agent = len(ag)
        n_unused = sum(1 for k in ag if k in unused)
        item_rows.append((s, "Size (operations)", rs["size"] or 14, n_agent, n_agent - n_unused, None, None, None))
        item_rows.append((s, "Time (min)", None, minutes(log), None, None, None, None))

    with open(OUT / "taskA-items.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["service", "dimension", "n_reference", "n_agent", "tp_or_active", "precision", "recall", "f1"])
        w.writerows([r[:5] + tuple(fmt(x) if isinstance(x, float) else x for x in r[5:]) for r in item_rows])
    with open(OUT / "taskA-pairs.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["service", "dimension", "n_reconciled", "agent_p", "agent_r", "agent_f1", "dev_p", "dev_r",
                    "dev_f1", "agent_missed", "agent_extra", "dev_missed", "dev_extra"])
        w.writerows([r[:3] + tuple(fmt(x) for x in r[3:9]) + r[9:] for r in pair_rows])
    with open(OUT / "taskA-provider-counts.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["service", "provider", "reconciled_ops", "agent_ops", "questionnaire_ops"])
        w.writerows(count_rows)
    ev = {}
    for d in {rdir(s) for s in SERVICES}:
        for r in csv.DictReader(open(d / "evidence-check.csv", encoding="utf-8")):
            s = r["file"].replace(".json", "")
            if rdir(s) == d:
                ev.setdefault(s, []).append(r["status"])
    with open(OUT / "taskA-evidence.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["service", "refs", "snapshot_ok", "snapshot_bad", "github_snapshot_commit",
                    "github_other_commit", "web", "share_snapshot_valid"])
        for s in SERVICES:
            st = ev.get(s, [])
            ok = sum(x in ("ok", "ok_file_only") for x in st)
            bad = sum(x in ("file_missing", "line_out_of_range", "unparseable") for x in st)
            w.writerow([s, len(st), ok, bad, st.count("github_snapshot_commit"), st.count("github_other_commit"),
                        st.count("web"), fmt(ok / (ok + bad)) if ok + bad else ""])
    with open(OUT / "taskA-item-diffs.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["service", "question", "kind", "item"])
        w.writerows(detail)

    print(f"{'service':14} {'dimension':20} ref  ag  tp     P     R    F1")
    for r in item_rows:
        print(f"{r[0]:14} {r[1]:20} {r[2] if r[2] is not None else '':>3} {r[3] if r[3] is not None else '':>3} "
              f"{r[4] if r[4] is not None else '':>3} {fmt(r[5]):>5} {fmt(r[6]):>5} {fmt(r[7]):>5}")
    print()
    for r in pair_rows:
        print(f"{r[0]:14} {r[1]:22} ref={r[2]:<3} agent F1={fmt(r[5]):5} dev F1={fmt(r[8]):5}"
              + (f"  | agent missed: {r[9]} | agent extra: {r[10]} | dev missed: {r[11]} | dev extra: {r[12]}" if VERBOSE else ""))
    print()
    for r in count_rows:
        print(f"{r[0]:14} ops to {r[1]:20} reconciled={r[2]:<3} agent={r[3]:<3} questionnaire={r[4]}")
    if VERBOSE:
        print()
        for d in detail:
            print(" | ".join(d))


if __name__ == "__main__":
    main()
