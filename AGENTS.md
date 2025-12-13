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

If you want, I can additionally scaffold:
- a `devcontainer.json` and `postCreateCommand` to match Codespaces setup,
- a GitHub Actions job that enforces `AGENTS.md` rules by linting PR diffs,
- auto-generated PR templates for agent-driven changes.
