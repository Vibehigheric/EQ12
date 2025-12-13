EQ12 — Macrium Reflect Integration

Overview

This directory contains conservative wrappers to integrate Macrium Reflect backups and viBoot tests into the EQ12 automation stack.

Files

- `eq12_reflect_backup.ps1` — triggers Full weekly / Incremental daily backups using the Macrium Reflect PowerShell module (placeholder cmdlets used; replace with exact vendor cmdlets if needed). Logs JSON to `C:\EQ12\logs\macrium.log`. On failure, calls `eq12-tg` to send a Telegram alert.

- `eq12_reflect_test.ps1` — uses `eq12_viboot_stage.ps1` to stage the latest backup in viBoot and run two EQ12 check commands inside the VM: `eq12-elite-run --dry-run` and `eq12-build-dashboard --check`. Results and captured output are appended to `C:\EQ12\logs\viboot_test.log`.

- `eq12_reflect_integration.ps1` — a tiny wrapper you can call from `run_daily_maintenance_now.ps1` to wire Reflect backups and weekly viBoot tests into your daily maintenance flow.

Safety and defaults

- Default mode across scripts is conservative: pass `-Verify` to do a dry-run without making changes.
- Scripts log JSON objects with fields `{ ts, status, msg, extra }` to `C:\EQ12\logs`.
- Scripts do not delete or overwrite backup images. viBoot staging is used to test backups read-only.
- Hyper-V and viBoot commands are placeholders in some locations; replace with your site-specific viBoot CLI syntax if necessary.

Recommended next steps

1. Update the Macrium-specific cmdlet names in `eq12_reflect_backup.ps1` to match your Reflect PowerShell module (cmdlet names vary by version).
2. Ensure `eq12-tg` (Telegram helper) is on PATH and callable by these scripts. It should accept a single string argument.
3. Test the scripts in `-Verify` mode first. Then run a manual incremental backup and monitor `C:\EQ12\logs\macrium.log`.
4. To wire into your daily run, add this line to your `run_daily_maintenance_now.ps1` at the appropriate place:

    & 'C:\EQ12\scripts\eq12_reflect_integration.ps1' -Verify:$false

Contact

If you want, I can update `run_daily_maintenance_now.ps1` directly (backup first) to insert the above call. Let me know if you want me to do that and whether to assume a default backup definition name for Reflect or use your custom one.
