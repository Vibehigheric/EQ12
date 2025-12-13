import logging
from pathlib import Path

# Set up logging
logger = logging.getLogger(__name__)

# sanitizer_v8.py - aggressive line-level sanitizer: comment any line containing PowerShell markers
orig = Path(r"C:/EQ12/EdgeGodParlays/ai_betting_bot_stealth_final_flask_pro.py.merged-candidate.py")
out = orig.with_suffix(".sanitized8.py")
if not orig.exists():
    print("ERROR: original not found", orig)
    raise SystemExit(1)
text = orig.read_text(encoding="utf-8", errors="replace")
lines = text.splitlines()
ps_markers = [
    "$",
    "{",
    "}",
    "Copy-Item",
    "Move-Item",
    "Start-Process",
    "New-Item",
    "Set-Alias",
    "Register-ScheduledTask",
    "Import-Module",
    "`",
]

out_lines = []
for ln in lines:
    if any(marker in ln for marker in ps_markers):
        out_lines.append("# [sanitized-ps] " + ln)
    else:
        out_lines.append(ln)

out.write_text("\n".join(out_lines), encoding="utf-8")
print("WROTE:", out)

# try compile
import py_compile

try:
    py_compile.compile(str(out), doraise=True)
    print("PY_COMPILE sanitized8: OK")
except Exception as e:
    print("PY_COMPILE sanitized8: FAILED")
    logger.info(e)
    raise SystemExit(2)
