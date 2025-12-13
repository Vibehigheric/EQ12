# EQ12 GitHub Extensions

This repo extends GitHub with:
- **Guardian CI**: GPG-sign verification, pytest, Pester, artifacts.
- **Nightly**: dry-run automation, dashboard artifacts, Telegram alerts.
- **IssueOps**: `/eq12 secrets:check`, `/eq12 nightly:dryrun`, `/eq12 gpg:verify`.

## How to use
1. Add secrets in GitHub → Settings → Secrets → Actions:
   - `ODDS_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`
2. Commit these files and push.
3. Use `/eq12 secrets:check` in a PR comment to validate the environment.
4. Check Guardian CI results on PRs; only signed commits and passing tests can merge (with branch protection).
