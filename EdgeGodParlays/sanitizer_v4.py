import logging
import re
from pathlib import Path

# Set up logging
logger = logging.getLogger(__name__)

# sanitizer_v4.py - drop lines containing PowerShell cmdlets entirely
orig = Path(r"C:/EQ12/EdgeGodParlays/ai_betting_bot_stealth_final_flask_pro.py.merged-candidate.py")
out = orig.with_suffix(".sanitized4.py")
if not orig.exists():
    print("ERROR: original not found", orig)
    raise SystemExit(1)
text = orig.read_text(encoding="utf-8", errors="replace")
lines = text.splitlines()
cmdlets = [
    "Copy-Item",
    "Move-Item",
    "Set-Item",
    "Get-Item",
    "Start-Process",
    "New-Item",
    "Set-Alias",
    "Register-ScheduledTask",
    "Import-Module",
    "Get-ChildItem",
    "Remove-Item",
]
out_lines = []
for ln in lines:
    if any(cmd in ln for cmd in cmdlets):
        # drop the line
        continue
    # neutralize lines with leading $ or `
    if ln.lstrip().startswith("$") or "`" in ln:
        out_lines.append("# [sanitized] " + ln)
        continue
    # neutralize common PowerShell operators
    if re.search(r"\s-(replace|like|contains|join|match|split|eq|ne|lt|gt)\b", ln):
        out_lines.append("# [sanitized] " + ln)
        continue
    out_lines.append(ln)

out.write_text("\n".join(out_lines), encoding="utf-8")
print("WROTE:", out)

import py_compile

try:
    py_compile.compile(str(out), doraise=True)
    print("PY_COMPILE sanitized4: OK")
except Exception as e:
    print("PY_COMPILE sanitized4: FAILED")
    logger.info(e)
    raise SystemExit(2)
