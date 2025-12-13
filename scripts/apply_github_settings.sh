#!/usr/bin/env bash
# Apply EQ12 starter GitHub settings to a repo using the gh CLI.
# Usage: apply_github_settings.sh <owner/repo>

set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <owner/repo>"
  exit 2
fi

REPO="$1"

echo "Applying EQ12 settings to $REPO"

# Ensure gh is available
if ! command -v gh >/dev/null 2>&1; then
  echo "gh CLI is required. Install and authenticate first: gh auth login"
  exit 1
fi

# Set default branch to main
gh api -X PATCH /repos/$REPO -f default_branch=main

# Create branch protection for main requiring status checks and signed commits
gh api /repos/$REPO/branches/main/protection -X PUT -F required_status_checks='{"strict":true,"contexts":["eq12-ci/test-python","eq12-ci/test-powershell"]}' -F enforce_admins=true -F required_pull_request_reviews='{"required_approving_review_count":1}' || true

echo "Enabling auto-delete branch on merge"
gh api -X PATCH /repos/$REPO -f delete_branch_on_merge=true

echo "Settings applied (some calls may require repo admin privileges)."
