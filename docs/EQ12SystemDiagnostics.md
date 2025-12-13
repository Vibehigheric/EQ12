# EQ12 System Diagnostics Runner

`EQ12SystemDiagnostics` is a VB.NET console utility that orchestrates startup verification, Chrome automation checks, API credential validation, program discovery, system statistics, and basic syntax linting for PowerShell/Python scripts. It can also bootstrap Full-Archive search requests against X (Twitter) to collect sports-related tweets for betting analytics.

## Location

- Project: `visual_studio_projects/EQ12SystemDiagnostics`
- Entry point: `Program.vb`
- Target framework: .NET 8.0 (console app)

## Building / Running

```powershell
cd C:\EQ12\visual_studio_projects\EQ12SystemDiagnostics
# Build
cmd /c "dotnet build"
# Run diagnostics only
cmd /c "dotnet run -- --repo-root C:\EQ12"
# Run diagnostics and generate sports tweet samples
cmd /c "dotnet run -- --repo-root C:\EQ12 --sports --max-tweets 250 --sports-output C:\EQ12\data\sports_queries.json"
```

## Checks Performed

| Check | Purpose | Output |
|-------|---------|--------|
| EQ12 Startup Files | Verifies key scripts/directories exist (`Start-EQ12-GODSTACK-Clean.ps1`, `logs`, `tests`, etc.). | Marks missing elements with warnings and remediation steps. |
| Chrome Automation Setup | Confirms Chrome binary presence and governance automation script. | Fails if Chrome is not installed. |
| API Credential Configuration | Confirms critical variables (`X_BEARER_TOKEN`, `ODDS_API_KEY`, `OPENAI_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`). | Warns for missing entries. |
| Program Discovery | Counts PowerShell/Python automation scripts under `scripts/`. | Warns if scripts directory missing. |
| System Statistics | Counts `.py`, `.ps1`, `.vb`, `.json` files repo-wide. | Displays aggregated totals. |
| Syntax Validation | Uses PowerShell parser + `python -m compileall` to detect syntax breaks. | Emits warnings when parse errors occur. |

## Sports Query Mode

When launched with `--sports` the utility:

1. Loads sports/team keywords from `configs\sports_keywords.txt` (or fallback list).
2. Builds query batches that respect X API query length limits.
3. Calls the X v2 Full-Archive Search endpoint (`https://api.x.com/2/tweets/search/all`).
4. Saves the results (tweets + raw responses) to the provided path.

Environment requirement: `X_BEARER_TOKEN` must contain a valid Academic Research bearer token.

## Extending

- Add new diagnostics by implementing `IDiagnosticCheck` and registering it in `Main`.
- Update `CriticalVars` in `ApiConfigurationCheck` for additional secrets.
- Update `KeywordsFallback` in `SportsQueryCoordinator` or provide a custom `--keywords` file.

## Safety

- PowerShell syntax scan writes a temporary `.ps1` in `%TEMP%` and removes it after execution.
- The tool only reads files; it will not mutate repo contents except for optional sports query output.

## Related Utilities

- `scripts\export_postman_environment.ps1` – Keep Postman aligned with EQ12 credentials.
- `EQ12_Interactive_Launcher.ps1` – Manual entry point that this diagnostics suite supplements.

