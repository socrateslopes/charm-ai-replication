#!/usr/bin/env python3
"""Rebuild the Task A code snapshot exactly as it was in the first execution.

Reads execution/results/snapshots.csv (written by P0), clones each repository
once (without checking out files), and exports every recorded folder at the
recorded commit with `git archive`, so the new workspace has the same files
and no git history. Writes a manifest with the tree hash of each folder, so
the rebuild can be compared with the original commits.

Usage:
    python3 rebuild_snapshot.py <snapshots.csv> <workspace_dir> <manifest_out.csv>

Example:
    python3 ~/charm-kit-rerun/execution-rerun/tools/rebuild_snapshot.py \
        ~/charm-kit-rerun/execution/results/snapshots.csv ~/charm-rerun/A \
        ~/charm-kit-rerun/execution-rerun/results/A/rebuild-manifest.csv
"""
import csv
import subprocess
import sys
from pathlib import Path

CLONES = Path("/tmp/charm-rerun-clones")


def run(*args, **kw):
    return subprocess.run(args, check=True, capture_output=True, text=True, **kw).stdout.strip()


def main(manifest, workspace, out):
    workspace, out = Path(workspace).expanduser(), Path(out).expanduser()
    rows = list(csv.DictReader(open(Path(manifest).expanduser(), encoding="utf-8")))
    CLONES.mkdir(parents=True, exist_ok=True)
    results = []
    for remote in sorted({r["remote"] for r in rows}):
        name = remote.rstrip("/").split("/")[-1].removesuffix(".git")
        clone = CLONES / name
        if not clone.exists():
            print(f"cloning {remote}")
            run("git", "clone", "--quiet", "--filter=blob:none", "--no-checkout", remote, str(clone))
        else:
            run("git", "-C", str(clone), "fetch", "--quiet", "origin")
        for r in (x for x in rows if x["remote"] == remote):
            rel = r["dest"].split("/A/", 1)[1]            # repos/<service>/<folder>
            dest = workspace / rel
            if dest.exists():
                sys.exit(f"{dest} already exists; start from an empty workspace")
            dest.mkdir(parents=True)
            sha, sub = r["commit_sha"], r["subdir"]
            archive = ["git", "-C", str(clone), "archive", sha] + ([] if sub == "." else [sub])
            p1 = subprocess.Popen(archive, stdout=subprocess.PIPE)
            subprocess.run(["tar", "-x", "-C", str(dest)], stdin=p1.stdout, check=True)
            if p1.wait() != 0:
                sys.exit(f"git archive failed for {remote} {sha} {sub}")
            tree = run("git", "-C", str(clone), "rev-parse", f"{sha}:{'' if sub == '.' else sub}")
            files = sum(1 for f in dest.rglob("*") if f.is_file())
            results.append({"dest": rel, "remote": remote, "subdir": sub, "commit_sha": sha,
                            "tree": tree, "files": files})
            print(f"  {rel}: {files} files at {sha[:10]}")
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(results[0]))
        w.writeheader()
        w.writerows(results)
    git_dirs = list(workspace.rglob(".git"))
    print(f"\n{len(results)} folders rebuilt (original manifest: {len(rows)}); .git folders: {len(git_dirs)}")
    print(f"Manifest: {out}")
    if len(results) != len(rows) or git_dirs:
        sys.exit("CHECK FAILED")
    print("OK")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])
