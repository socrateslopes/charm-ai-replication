#!/usr/bin/env python3
"""Check that the evidence cited in Task A outputs exists in the snapshot.

For every JSON file in <run_dir>, walks all "evidence" arrays and checks that
each reference of the form repos/<path>:<line> or repos/<path>:<start>-<end>
points to an existing file and to lines within that file. References to
GitHub (github:<owner>/<repo>@<sha>:<path>:<line>) are classified as
github_snapshot_commit when <sha> is a commit in <workspace>/inputs/
snapshots.csv and github_other_commit otherwise (to be checked by hand);
web:<url> references are counted as web. Items with an empty evidence array
are also counted. Prints a summary and writes evidence-check.csv into
<run_dir>.

Usage:
    python3 check_evidence.py <workspace_root> <run_dir>

Example:
    python3 check_evidence.py ~/charm-study/A ~/charm-kit/execution/results/A
"""
import csv
import json
import re
import sys
from pathlib import Path

REF = re.compile(r"^(?P<path>.+?)(?::(?P<start>\d+)(?:-(?P<end>\d+))?)?$")
GITHUB = re.compile(r"^github:[^@\s]+@(?P<sha>[0-9a-f]{7,40})\b", re.I)


def walk(node, where, out):
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "evidence":
                out.append((where, value if isinstance(value, list) else [value]))
            else:
                walk(value, f"{where}.{key}", out)
    elif isinstance(node, list):
        for i, value in enumerate(node):
            walk(value, f"{where}[{i}]", out)


def snapshot_shas(root):
    manifest = root / "inputs" / "snapshots.csv"
    if not manifest.is_file():
        return set()
    with manifest.open(newline="", encoding="utf-8") as f:
        return {row["commit_sha"].lower() for row in csv.DictReader(f) if row.get("commit_sha")}


def check(root, ref, cache, shas):
    ref = ref.strip()
    if ref.lower().startswith("web:"):
        return "web"
    if ref.lower().startswith("github:"):
        g = GITHUB.match(ref)
        if not g:
            return "github_no_commit"
        sha = g.group("sha").lower()
        return "github_snapshot_commit" if any(s.startswith(sha) for s in shas) else "github_other_commit"
    m = REF.match(ref)
    if not m:
        return "unparseable"
    path = root / m.group("path")
    if not path.is_file():
        return "file_missing"
    if m.group("start") is None:
        return "ok_file_only"
    if path not in cache:
        with path.open("rb") as f:
            cache[path] = sum(1 for _ in f)
    end = int(m.group("end") or m.group("start"))
    return "ok" if 1 <= int(m.group("start")) <= end <= cache[path] else "line_out_of_range"


def main(root, run_dir):
    root, run_dir = Path(root), Path(run_dir)
    rows, cache, shas = [], {}, snapshot_shas(root)
    for jf in sorted(run_dir.glob("*.json")):
        items = []
        try:
            data = json.loads(jf.read_text(encoding="utf-8"))
        except ValueError as e:
            rows.append({"file": jf.name, "item": "", "ref": str(e)[:80], "status": "invalid_json"})
            continue
        walk(data, jf.stem, items)
        for where, refs in items:
            if not refs or refs == [""]:
                rows.append({"file": jf.name, "item": where, "ref": "", "status": "no_evidence"})
            for ref in refs:
                if ref:
                    rows.append({"file": jf.name, "item": where, "ref": ref, "status": check(root, ref, cache, shas)})
    out = run_dir / "evidence-check.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["file", "item", "ref", "status"])
        w.writeheader()
        w.writerows(rows)
    total = len(rows)
    counts = {}
    for r in rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    print(f"{total} references checked in {run_dir}")
    for status, n in sorted(counts.items()):
        print(f"  {status}: {n} ({100 * n / total:.1f}%)" if total else f"  {status}: {n}")
    print(f"Details: {out}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(*sys.argv[1:])
