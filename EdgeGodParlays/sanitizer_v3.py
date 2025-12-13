import logging
import re
from pathlib import Path

# Set up logging
logger = logging.getLogger(__name__)

# sanitizer_v3.py - aggressive sanitizer
# - removes UTF-8 BOM
# - comments out lines starting with $ (with optional BOM)
# - comments out heredoc markers, PowerShell operators and other non-Python tokens
# - writes .sanitized3.py and attempts to py_compile it
orig = Path(r"C:/EQ12/EdgeGodParlays/ai_betting_bot_stealth_final_flask_pro.py.merged-candidate.py")
out = orig.with_suffix(".sanitized3.py")
if not orig.exists():
    print("ERROR: original not found", orig)
    raise SystemExit(1)
raw = orig.read_bytes()
# remove BOM if present
if raw.startswith(b"\xef\xbb\xbf"):
    raw = raw[3:]
text = raw.decode("utf-8", errors="replace")
lines = text.splitlines()

out_lines = []
for ln in lines:
    s = ln.lstrip()
    # comment out PowerShell variable lines starting with $ (allow BOM or stray unicode)
    if s.startswith("$"):
        out_lines.append("# [sanitized] " + ln)
        continue
    # comment lines likely to be PowerShell heredoc markers
    if re.match(r"^\s*(@'|@\"|'@|\"@)\s*$", ln):
        out_lines.append("# [sanitized] " + ln)
        continue
    # comment lines with common PS operators or -replace
    if re.search(r"\s-(replace|like|contains|join|match|split|eq|ne|lt|gt)\b", ln):
        out_lines.append("# [sanitized] " + ln)
        continue
    # comment lines with backticks or unescaped windows-style variable + backslash-heavy strings that look like PS
    if "`" in ln or re.search(r"\$\w+\s*=", ln):
        out_lines.append("# [sanitized] " + ln)
        continue
    # comment lines that are very long with mostly non-ascii characters or contain typical PS cmdlets like Start-Process, New-Item
    if re.search(
        r"\b(Start-Process|New-Item|Set-Alias|Get-ChildItem|Register-ScheduledTask|Import-Module)\b",
        ln,
        re.I,
    ):
        out_lines.append("# [sanitized] " + ln)
        continue
    # otherwise keep
    out_lines.append(ln)

out.write_text("\n".join(out_lines), encoding="utf-8")
print("WROTE:", out)

# try compile
import py_compile

try:
    py_compile.compile(str(out), doraise=True)
    print("PY_COMPILE sanitized3: OK")
except Exception as e:
    print("PY_COMPILE sanitized3: FAILED")
    logger.info(e)
    raise SystemExit(2)
