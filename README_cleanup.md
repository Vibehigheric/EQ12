EQ12 Cleanup - README

What was done
- Sensitive files `EdgeGodParlays/creds.json` and `EdgeGodParlays/.env` were moved to `keys/`.
- Duplicate and backup files (pattern: " - Copy", ".bak", "~", ".old") were moved to `archive_duplicates/` preserving relative structure.
- Small unified diffs were generated where a copy had a clear original to help review.
- `.gitignore` was updated to ignore `EdgeGodParlays/creds.json`, `EdgeGodParlays/.env`, and `keys/`.
- `eq12_inventory.txt` was regenerated to a concise list.

Where to look
- Manifest of keys: `keys_manifest.txt`
- Manifest of archives: `archive_manifest.txt`
- Run report: `eq12_cleanup_report.txt`

Restore instructions
- Use `eq12_restore.py --list` to see files in `keys/`.
- Use `eq12_restore.py --restore <filename>` to restore a file (it will restore to `EdgeGodParlays/` by default for known files).

Notes & recommendations
- Review diffs in `archive_duplicates/` before deleting archived copies.
- If you want to include/exclude additional patterns, update `eq12_cleanup.py` DUP_PATTERNS.
- Consider creating `requirements.txt` for reproducibility; venv created at `.venv`.
