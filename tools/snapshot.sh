#!/usr/bin/env bash
# Export a history-free snapshot of a repository (or one subdirectory of it)
# as of the last commit on a branch before a cutoff date, and append the
# provenance to a manifest.
#
# Usage:
#   snapshot.sh <local_clone> <branch> <subdir|.> "<cutoff, e.g. 2026-03-11 00:00 -0300>" <dest_dir> <manifest.csv>
#
# Example:
#   snapshot.sh ~/src/payments-api origin/main . "2026-03-11 00:00 -0300" \
#       ~/charm-study/A/repos/payments-api ~/charm-study/snapshots.csv
set -euo pipefail

clone="$1"; branch="$2"; subdir="$3"; cutoff="$4"; dest="$5"; manifest="$6"

git -C "$clone" fetch --quiet origin
sha=$(git -C "$clone" rev-list -1 --before="$cutoff" "$branch")
if [ -z "$sha" ]; then
  echo "No commit before $cutoff on $branch" >&2
  exit 1
fi
date_of_sha=$(git -C "$clone" show -s --format=%cI "$sha")
remote=$(git -C "$clone" remote get-url origin)

mkdir -p "$dest"
if [ "$subdir" = "." ]; then
  git -C "$clone" archive "$sha" | tar -x -C "$dest"
else
  git -C "$clone" archive "$sha" "$subdir" | tar -x -C "$dest"
fi

[ -f "$manifest" ] || echo "remote,branch,subdir,commit_sha,commit_date,cutoff,dest" > "$manifest"
echo "$remote,$branch,$subdir,$sha,$date_of_sha,$cutoff,$dest" >> "$manifest"
echo "Snapshot of $remote@$sha ($date_of_sha) -> $dest"
