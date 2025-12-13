⚡ EQ12 GODSTACK – GitHub CLI Governance Cheat-Sheet

This cheat-sheet lists the most useful **`gh` commands** for managing governance, security, and compliance in EQ12 GODSTACK.

---

## 🔑 Authentication & Setup

```bash
# Log in to GitHub CLI (once per machine)
gh auth login

# Confirm login
gh auth status

# Set default repo context
gh repo set-default Vibehigheric/edgegod-parlay
```

---

## 📌 Pull Requests

```bash
# List open PRs
gh pr list

# List PRs with labels (show sensitive PRs)
gh pr list --json number,title,labels,author

# View PR details (shows checks, labels, reviewers)
gh pr view <PR_NUMBER> --web

# Checkout a PR locally for testing
gh pr checkout <PR_NUMBER>

# Approve or request changes (must be CODEOWNER if sensitive)
gh pr review <PR_NUMBER> --approve
gh pr review <PR_NUMBER> --request-changes -b "Explain what needs fixing"

# Check PR status (governance gates)
gh pr checks <PR_NUMBER>
```

---

## 🛡 Governance Workflows

```bash
# List workflows
gh workflow list

# View workflow details
gh workflow view ci-all-in-one.yml

# Run a workflow manually
gh workflow run ci-all-in-one.yml
gh workflow run security-scan.yml
gh workflow run governance-board-sync.yml

# View workflow runs
gh run list --workflow=ci-all-in-one.yml

# Re-run latest failed workflow
gh run rerun <RUN_ID>

# View logs for a specific run
gh run view <RUN_ID> --log
```

---

## 🔒 Secrets Management

```bash
# List repo secrets
gh secret list

# Set a secret
gh secret set TG_TOKEN --body "your-token-here"
gh secret set TG_CHAT_ID --body "@yourchannel"
gh secret set OPENAI_SERVICE_KEY --body "sk-..."

# Remove a secret
gh secret remove CODECOV_TOKEN

# List environment secrets (if using environments)
gh secret list --env production
```

---

## 📊 Governance Board Integration

```bash
# List issues (review checklists auto-created by workflows)
gh issue list --label "review-needed"
gh issue list --label "governance"

# Open a specific issue/PR review checklist
gh issue view <ISSUE_NUMBER> --web

# Create a governance issue manually
gh issue create --title "Compliance Review: PR #123" --body "Review checklist..."

# Add governance labels manually (if needed)
gh pr edit <PR_NUMBER> --add-label "⚠ Sensitive: Betting"
gh pr edit <PR_NUMBER> --add-label "review-needed"
```

---

## 🧪 Security & Compliance

```bash
# View Dependabot alerts
gh api repos/Vibehigheric/edgegod-parlay/dependabot/alerts

# Trigger CodeQL scan
gh workflow run codeql-analysis.yml

# Trigger security scan workflow
gh workflow run security-scan.yml

# Trigger compliance audit manually
gh workflow run compliance.yml

# Check for secret scanning alerts
gh api repos/Vibehigheric/edgegod-parlay/secret-scanning/alerts
```

---

## 🚨 Common Governance Checks

```bash
# Check if a PR passed all governance gates
gh pr checks <PR_NUMBER>

# View CI/CD logs for a run
gh run view <RUN_ID> --log

# Show labels on a PR (to confirm auto-labeler applied)
gh pr view <PR_NUMBER> --json labels

# List sensitive PRs specifically
gh pr list --json number,title,labels | jq '.[] | select(.labels[]?.name | contains("Sensitive"))'

# Check CODEOWNERS for required reviewers
gh api repos/Vibehigheric/edgegod-parlay/contents/.github/CODEOWNERS
```

---

## 📈 Monitoring & Metrics

```bash
# Get repository statistics
gh api repos/Vibehigheric/edgegod-parlay --template '{{.open_issues_count}} open issues'

# List recent commits to main
gh api repos/Vibehigheric/edgegod-parlay/commits --template '{{range .}}{{.commit.message}} ({{.commit.author.name}}){{"\n"}}{{end}}'

# Check branch protection rules
gh api repos/Vibehigheric/edgegod-parlay/branches/main/protection

# List repository collaborators
gh api repos/Vibehigheric/edgegod-parlay/collaborators
```

---

## 🔄 EQ12 Automation Integration

```bash
# PowerShell wrapper for daily governance check
function Check-EQ12Governance {
    $openPRs = gh pr list --json number,title,labels,author | ConvertFrom-Json
    $sensitivePRs = $openPRs | Where-Object { $_.labels.name -contains "⚠ Sensitive: Betting" -or $_.labels.name -contains "⚠ Sensitive: Cannabis" -or $_.labels.name -contains "⚠ Sensitive: Credit" }
    
    Write-Output "📊 EQ12 Governance Status:"
    Write-Output "   Open PRs: $($openPRs.Count)"
    Write-Output "   Sensitive PRs: $($sensitivePRs.Count)"
    
    if ($sensitivePRs.Count -gt 0) {
        Write-Output "⚠ Sensitive PRs requiring review:"
        $sensitivePRs | ForEach-Object { Write-Output "   PR #$($_.number): $($_.title)" }
    }
}

# Bash wrapper for Linux/Codespaces
function check_eq12_governance() {
    local open_prs=$(gh pr list --json number | jq length)
    local sensitive_prs=$(gh pr list --json labels | jq '[.[] | select(.labels[]?.name | contains("Sensitive"))] | length')
    
    echo "📊 EQ12 Governance Status:"
    echo "   Open PRs: $open_prs"
    echo "   Sensitive PRs: $sensitive_prs"
    
    if [ "$sensitive_prs" -gt 0 ]; then
        echo "⚠ Sensitive PRs requiring review:"
        gh pr list --json number,title,labels | jq -r '.[] | select(.labels[]?.name | contains("Sensitive")) | "   PR #\(.number): \(.title)"'
    fi
}
```

---

## ✅ Best Practices

- Always run `gh pr checks <PR_NUMBER>` before approving a sensitive PR.
- Use `gh secret list` regularly to confirm required secrets exist.
- Automate daily/weekly compliance runs via EQ12 Task Scheduler calling `gh workflow run ...`.
- For sensitive stacks (`betting/`, `cannabis/`, `credit/`), require **CODEOWNERS + Copilot Review** before approval.
- Use JSON output (`--json`) for scripting and automation.
- Set up aliases for frequently used commands.

---

## 🚀 Advanced Usage

```bash
# Create custom aliases
gh alias set prs 'pr list --json number,title,labels,author'
gh alias set sensitive-prs 'pr list --json number,title,labels | jq ".[] | select(.labels[]?.name | contains(\"Sensitive\"))"'
gh alias set failing-checks 'pr list --json number,title | jq ".[] | select(.checks.state == \"failure\")"'

# Use with EQ12 Task Scheduler (Windows)
schtasks /create /tn "EQ12-Governance-Check" /tr "powershell -Command 'Check-EQ12Governance'" /sc daily /st 09:00

# Use with cron (Linux/Codespaces)
echo "0 9 * * * /usr/local/bin/gh pr list --json number,title,labels" | crontab -
```

---

*This cheat-sheet covers the essential GitHub CLI commands for maintaining governance, security, and compliance in your EQ12 GODSTACK. Keep it handy for daily operations!*