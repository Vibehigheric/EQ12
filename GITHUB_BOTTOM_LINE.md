# EQ12 GitHub Bottom Line (Hardcoded)

- Operate under a single personal account with GitHub Pro (2FA required).
- Build and collaborate in an organization named "EQ12" (GitHub Team now; upgrade to Enterprise Cloud if/when SSO/compliance is needed).
- Keep code private by default: `eq12-core`, `eq12-actions`, `eq12-marketplace-app` (private). Keep `eq12-docs` public.
- Enforce org security: branch protections, required checks (ruff, bandit, pip-audit, tests), Dependabot, secret scanning/push protection.
- Distribute via GitHub Packages/Releases (org-scoped). Use Environments (staging/prod) with required reviewers and environment secrets (ODDS_API_KEY, OpenAI, etc.).
- Control CI spend: use workflow concurrency and ACTIONS_BUDGET_LOCK gate; schedule heavy jobs nightly.
- Require GitLens review in PRs; use Teams for access (no direct user grants).
