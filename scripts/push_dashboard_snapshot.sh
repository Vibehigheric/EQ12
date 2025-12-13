#!/usr/bin/env bash
# Push dashboard snapshot (logs/dashboard_snapshot.json) to dashboard-snapshots branch
# Usage: push_dashboard_snapshot.sh [--repo owner/repo]

set -euo pipefail

REPO=""
if [ "$#" -ge 1 ]; then
  REPO="$1"
fi

BRANCH="dashboard-snapshots"

if [ ! -f logs/dashboard_snapshot.json ]; then
  echo "No logs/dashboard_snapshot.json found"
  exit 0
fi

if [ -z "$REPO" ]; then
  # try to infer from git
  REPO=$(git config --get remote.origin.url || true)
fi

# create orphan branch and commit snapshot
TMP_DIR=$(mktemp -d)
cp logs/dashboard_snapshot.json "$TMP_DIR/"
cd "$TMP_DIR"
git init
git checkout -b "$BRANCH"
mkdir -p logs
mv dashboard_snapshot.json logs/
git add logs/dashboard_snapshot.json
git commit -m "chore: update dashboard snapshot [ci skip]"

if [ -n "$REPO" ]; then
  # convert git url to https remote if needed
  if echo "$REPO" | grep -qE "git@github.com:"; then
    REPO_URL=$(echo "$REPO" | sed -E 's/git@github.com:(.*)\.git/https:\/\/github.com\/\1.git/')
  else
    REPO_URL="$REPO"
  fi
  git push --force "$REPO_URL" "$BRANCH"
else
  echo "No remote repository specified; snapshot committed locally in $TMP_DIR"
fi

echo "Dashboard snapshot push complete."

*** End Patch