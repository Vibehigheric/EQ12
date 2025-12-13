# EQ12 VS Code Automation Playbook

This guide maps the new automation assets to the three primary personas working inside the EQ12 stack.

## 1. Sports Bettors

- **Command Center Script**: `python scripts/sports/eq12_sports_command_center.py` pulls odds, injuries, and sentiment to generate dynamic edges. Use the VS Code task **EQ12: Sports Edge Pipeline** to run it with a single shortcut.
- **Season Awareness**: `configs/sports_season_clock.json` is auto-generated and refreshed with current year windows (`--refresh-calendar`).
- **Outputs**: edges written to `data/sports_edges.json` and logged under `logs/sports/`.
- **Environment**: populate `ODDS_API_KEY` and `X_BEARER_TOKEN` for real feeds; otherwise the script emits placeholders.
- **Notebook Workflow**: leverage `EQ12_Expert_System_Analysis.ipynb` alongside the new pipeline for rapid backtesting.

## 2. Control Technicians

- **Toolkit**: `scripts/control/control_system_toolkit.ps1`
  - `-Diagnostics` checks dependencies, versions, and PLC config inventory.
  - `-Package` zips deployment artifacts into `artifacts/`.
  - `-Config` conversion mode supports JSON↔CSV and YAML→JSON conversions (installs `powershell-yaml` on demand).
- **VS Code Task**: run **EQ12: Control Diagnostics** to execute checks from the command palette.
- **Version Control**: continue using Git integration in VS Code to manage ladder logic/config changes; the toolkit logs to `logs/control/` for audit trails.

## 3. Freelance Coders

- **Project Scaffold**: `python scripts/freelance/freelance_scaffold.py <name> --type {web,data,api}` spins up opinionated skeletons with optional dependency installation.
- **VS Code Task**: **EQ12: Freelance Scaffold** creates a sample project (`SampleProject`) and prints JSON summary for quick inspection.
- **Extensions**: the workspace now recommends PLC helpers, C++ tooling, Azure IoT, and Remote Explorer on top of the existing Python/DevOps stack.

## VS Code Tasks Summary

| Task | Persona | What it does |
| ---- | ------- | ------------- |
| EQ12: Sports Edge Pipeline | Sports bettor | Runs the command center to refresh edges (respects env vars). |
| EQ12: Control Diagnostics | Control technician | Executes PowerShell diagnostics and logs results. |
| EQ12: Freelance Scaffold | Freelancer | Generates a scaffolded project (web template by default). |

## Environment Prep

Set these variables in your shell profile or via the Postman export helper:

```powershell
setx ODDS_API_KEY "<your odds api key>"
setx X_BEARER_TOKEN "<academic bearer token>"
setx EQ12_REPO_ROOT "C:\EQ12"
```

## Tips & Tricks

- Map tasks to VS Code keyboard shortcuts (see `.vscode/keybindings.json`) for one-tap execution.
- Use Remote Containers or WSL for isolated control-system simulations.
- Pair the sports pipeline with `export_postman_environment.ps1` to keep API explorers synced.
- Drop custom keyword lists into `configs/sports_keywords.txt` for hyper-specific sentiment tracking.

All additions respect existing EQ12 logging (logs under `logs/`) and data directory conventions, so they slide into current automation/CI flows.
