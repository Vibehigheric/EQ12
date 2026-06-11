# AGENTS.md — EQ12 project agent onboarding

This file is intended for AI agents, Copilot/Codex, and human contributors who will act as autonomous helpers for the EQ12 stack. Treat the agent as a new teammate: provide context, a strict contract, clear examples, and success criteria.

---

## 1) Project overview

EQ12 is a lightweight automation and scraping/dashboard stack focused on getting timely data into a small dashboard. It includes:
- Scrapers and utilities (Python) under `scripts/` and `scraper_starter/`.
- PowerShell utilities and wrappers under `scripts/` for Windows automation.
- Tests in `tests/` (`pytest`) and `tests/pester/` (Pester).
- CI workflows under `.github/workflows/` and devcontainer config under `.devcontainer/`.

Target audience: developers who need a reproducible scraping/dashboard environment that runs locally and in Codespaces.

---

## 2) Tech stack

- Python 3.12 (main scripts, scrapers)
- PowerShell (automation, wrappers, Pester tests)
- Playwright (browser automation)
- Transformers / Hugging Face (ML tasks)
- GitHub Actions (CI)
- Optional: Node.js for Codex CLI

---

## 3) Coding standards (strict)

- Python: use argparse + logging for CLIs. Use type hints where practical. Prefer f-strings. Follow PEP8 (4-space indentation).
- PowerShell: always use `CmdletBinding()` for advanced functions. Prefer explicit parameter types and `Write-Error`/`Write-Verbose`.
- Secrets: never hardcode. Read from env variables: `ODDS_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `OPENAI_API_KEY`, `CODEX_API_KEY`.
- Logging: always write JSON snapshots to `C:\EQ12\logs` (Windows) or `/workspaces/EQ12/logs` (Codespaces). Use UTC timestamps.
- Commits: require signed commits (`git commit -S`). CI should verify signatures.
- Tests: every new feature or bugfix must include pytest and Pester tests where relevant.

---

## 4) Repository layout (short)

- `scripts/` — main runnable scripts (both .py and .ps1 wrappers)
- `tests/` — pytest files (unit/integration)
- `tests/pester/` — Pester tests for PowerShell
- `logs/` or `C:\EQ12\logs` — runtime snapshots and artifacts
- `.github/workflows/` — CI jobs
- `COPILOT_PROMPT.md`, `AGENTS.md` — project-level agent instructions

---

## 5) GPT-5 Enhanced Agent-to-Human Contract

- **Inputs**: Repository file paths, explicit user requirements, environment variables, and reasoning effort level (minimal/medium/high)
- **Outputs**: PR-ready code patches with structured reasoning traces, comprehensive tests, CI updates, and detailed execution plan with local commands
- **Error Modes**: Missing files → structured file search with exact paths; missing secrets → safe fallback with clear setup instructions; failing tests → root cause analysis with fix recommendations
- **Success Criteria**: All tests pass (`pytest` + `Invoke-Pester`), CI workflows validate, structured logs/snapshots in `logs` directory, and reasoning traces document decision points

### GPT-5 Agentic Enhancements
- **Tool Preambles**: Always begin with clear goal restatement and structured execution plan
- **Progress Updates**: Provide sequential narration of each step with confidence indicators
- **Uncertainty Handling**: Auto-proceed on high confidence (>80%), escalate on ambiguity (<70%)
- **Reasoning Persistence**: Maintain context across tool calls for more efficient workflows

---

## 6) GPT-5 Optimized Task Workflow Template

### Pre-Execution Planning
```xml
<task_execution_plan>
1. **Goal Clarification**: Rephrase user request in clear, actionable terms
2. **Context Gathering**: Parallel file search with targeted queries, avoid over-searching
3. **Execution Strategy**: Create structured plan with clear success criteria
4. **Risk Assessment**: Identify safe vs unsafe actions, set escalation triggers
</task_execution_plan>
```

### Execution Phase (Agentic Workflow)
1. **Structured Context Gathering**: Use parallel searches, cache results, early stop when sufficient context obtained
2. **Minimal Planning**: Write execution steps with clear checkpoints (not extensive todo lists for simple tasks)
3. **Targeted Implementation**: Make surgical edits with reasoning traces, prefer minimal changes over comprehensive rewrites
4. **Continuous Validation**: Run relevant test subsets after each significant change (pytest -q, targeted Pester tests)
5. **Completion Documentation**: Summarize changes with confidence indicators and any escalation needs

### GPT-5 Reasoning Effort Guidelines
- **Minimal Reasoning**: Simple fixes, direct implementations - maximum 2 tool calls, brief explanations
- **Medium Reasoning** (default): Standard development tasks - balanced exploration, structured planning
- **High Reasoning**: Complex refactors, multi-file changes - thorough analysis, comprehensive edge case coverage

### Agentic Persistence Patterns
```xml
<persistence>
- Keep going until task completely resolved before yielding to user
- Never stop on uncertainty — research most reasonable approach and document assumptions
- Only escalate on unsafe actions or when confidence drops below 70%
- Maintain reasoning context across multiple tool calls for efficiency
</persistence>
```

---

## 7) Examples & prompt templates

Example: Fix failing Pester pathing

```
Task: Fix Pester test that can't find scripts/eq12_firefox_bookmarks.ps1

Steps:
1. Compute $PSScriptRoot for the test file and derive repo root by taking parent of parent.
2. Join repo root with 'scripts\eq12_firefox_bookmarks.ps1'.
3. Add a BeforeAll block that throws a clear error if file missing.
4. Dot-source and assert function exists.

Success: `Invoke-Pester` returns pass.
```

Example: Scaffold new feature (Python)

```
Task: Add eq12_vpn_check.py and eq12_vpn_check.ps1 wrapper

Steps:
1. Create Python CLI with argparse+logging.
2. Read VPN_API_KEY from env and validate.
3. Add pytest for happy path and one edge case (missing API key).
4. Add Pester wrapper test that calls the PS wrapper script and asserts output.

Success: pytest + Invoke-Pester pass.
```

Prompt template for Codex/Copilot (use when invoking agent):

```
### CONTEXT
- Repo root: `/workspaces/EQ12` or `C:\EQ12`
- Files you're allowed to modify: scripts/, tests/, .github/

### TASK
Implement [short description].

### REQUIREMENTS
- Must use CmdletBinding() for PowerShell / argparse+logging for Python
- Read secrets from env var names: ODDS_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
- Add pytest and Pester tests

### SUCCESS CRITERIA
- Tests pass locally (pytest + Invoke-Pester)
- Logs saved to the repo logs folder

### EXAMPLE
- show small example of input/output if helpful
```

---

## 8) Advanced behaviors and tool integration

- When a long-running change is required (multi-file refactor), write a small migration plan and ask for confirmation.
- Prefer safe changes: if adding a secret-only behavior, provide a prompt fallback and clear docs for dev setup.
- Use `git commit -S` for all automated commits; if GPG isn't available in CI, create a signed-bot approach with a bot key and document it in `AGENTS.md`.

---

## 9) EDGEGOD Machine-Readable System Spec

EDGEGOD architecture must be maintained as machine-readable source-of-truth files before major Python module work starts.

### Required instruction order

1. Convert the active architecture into machine-readable files.
2. Use YAML, JSON, and SQL as the source of truth.
3. Do not start with Python-only implementation.
4. Generate specs first.
5. Generate code from specs.
6. Generate tests from specs.

### Required spec files

Create and maintain these files under `specs/` when missing:

- `specs/edgegod_system_spec.yaml`
- `specs/edgegod_database_schema.sql`
- `specs/edgegod_api_contracts.json`
- `specs/edgegod_orchestration_flow.yaml`
- `specs/edgegod_feature_registry.yaml`
- `specs/edgegod_model_registry.yaml`
- `specs/edgegod_live_state_events.yaml`
- `specs/edgegod_clv_ledger_schema.sql`
- `specs/edgegod_monte_carlo_schema.yaml`
- `specs/edgegod_agent_protocol.yaml`

### Source-of-truth rule

Specs are the source of truth. Python modules, workflows, database tables, tests, and reports must be generated or validated against the YAML, JSON, and SQL specs.

### EDGEGOD MLB operating requirements

- Modes:
  - `PREGAME_BUILD`: build slate, fetch openers, check pitchers, no betting release
  - `SLATE`: allowed bets `moneyline`, `total`, `team_total`
  - `LINEUP_LOCK`: allowed bets `moneyline`, `total`, `team_total`, `player_props`
  - `LIVE`: all market types allowed
  - `POSTGAME`: no betting release
  - `NO_BET_HOLD`: no betting release
- Data source priority:
  - `statcast`: exit velocity, launch angle, barrels, hard hit, xBA, xwOBA, bat speed, blast rate
  - `mlb_api`: schedule, lineups, game status, probable pitchers
  - `ballparkpal`: weather, park factor, HR factor
  - `odds`: moneyline, totals, team totals, props, live lines
- Readiness weights:
  - savant `0.15`
  - lineup `0.20`
  - pitcher `0.15`
  - bullpen `0.15`
  - weather `0.10`
  - market `0.15`
  - injury `0.10`
- Readiness thresholds:
  - release `0.80`
  - lean `0.65`
  - no-bet-hold `<0.65`
- Lineup confidence:
  - confirmed `1.00`
  - projected `0.70`
  - expected `0.55`
  - unknown `0.25`
- Bullpen fatigue formula:
  - yesterday `0.50`
  - two_days `0.30`
  - three_days `0.20`
- Monte Carlo minimum: `10000` runs
- CLV tracking fields:
  - `prediction_id`
  - `opening_odds`
  - `bet_odds`
  - `closing_odds`
  - `result`
  - `clv_percent`
  - `closing_edge_delta`
- Approval rules:
  - readiness min `0.80`
  - confidence min `0.70`
  - edge min `0.04`
  - stale data blocks release
  - unconfirmed lineups block props
  - missing pitchers block release

### Required generation order

1. Scan existing repo.
2. Create missing spec files.
3. Map existing code to spec.
4. Detect gaps between spec and code.
5. Create missing modules.
6. Patch existing modules.
7. Generate tests from spec.
8. Run tests.
9. Run workflows.

---

## 10) Safe Odds API Key Validation

When working on MLB or SGP workflows, cycle only odds API keys that are already configured and do it safely.

### Objective

- Test all configured odds API keys.
- Identify the first working key.
- Export only the selected working key to the active process environment.
- Write a masked health report.
- Never expose secrets in logs, artifacts, commits, or summaries.

### Allowed key sources

- GitHub Actions secrets
- local `.env`
- environment variables
- existing secret-manager style config already present in the repo

### Candidate environment variable names

- `THEODDSAPI_KEY`
- `THE_ODDS_API_KEY`
- `ODDS_API_KEY`
- `ODDSAPI_API_KEY`
- `SPORTS_ODDS_API_KEY`
- `EQ12_ODDS_API_KEY`

### Safety rules

- Never echo a full key.
- Never commit a key.
- Never write a full key to artifacts.
- Mask keys as first four and last four characters only.
- Do not brute-force unknown keys.
- Only test keys that are already configured.

### Required implementation

Create and maintain:

- `scripts/validate_odds_keys.py`
- `artifacts/mlb/odds_key_health.json`

### Validation behavior

- Endpoint: The Odds API MLB odds endpoint
- Scope:
  - sport `baseball_mlb`
  - regions `us`
  - markets `h2h`
  - odds format `american`
- Status mapping:
  - `200` with games => `VALID`
  - `200` with empty response => `VALID_EMPTY`
  - `401` => `INVALID_KEY`
  - `403` => `FORBIDDEN_OR_QUOTA`
  - `429` => `RATE_LIMITED`
  - `5xx` => `PROVIDER_ERROR`

### Output requirements

`artifacts/mlb/odds_key_health.json` must include:

- `env_name`
- `key_masked`
- `status`
- `http_status`
- `quota_remaining_if_available`
- `selected`
- `tested_at`

### Workflow integration rules

- Run `validate_odds_keys.py` before MLB or SGP odds fetch steps.
- Export the selected key to process env only.
- If no key is valid, continue in `NO_BET_HOLD`.
- Never fail the workflow only because an odds key is missing or invalid.
- Record odds provider status in the workflow summary.

### Required workflow targets

- `.github/workflows/eq12-daily.yml`
- `.github/workflows/sgps.yml`

### MLB fallback behavior

If no valid odds API key is available, the correct output is:

```text
NO RELEASE-GRADE MLB PLAYS TODAY
Reason: no valid odds API key available
Mode: NO_BET_HOLD
```
10. Produce MLB artifacts.

### Final deliverable checklist

- specs created
- code created from specs
- tests created from specs
- mismatches found
- mismatches fixed
- database schema created
- API contract created
- orchestration flow created
- MLB today artifacts created
- next scheduled pipeline run identified

---

If you want, I can additionally scaffold:
- a `devcontainer.json` and `postCreateCommand` to match Codespaces setup,
- a GitHub Actions job that enforces `AGENTS.md` rules by linting PR diffs,
- auto-generated PR templates for agent-driven changes.
