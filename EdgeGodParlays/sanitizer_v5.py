import logging
import re
from pathlib import Path

# Set up logging
logger = logging.getLogger(__name__)

# sanitizer_v5.py - targeted sanitizer for '@' heredoc markers and remaining PS cmdlets
orig = Path(r"C:/EQ12/EdgeGodParlays/ai_betting_bot_stealth_final_flask_pro.py.merged-candidate.py")
out = orig.with_suffix(".sanitized5.py")
if not orig.exists():
    print("ERROR: original not found", orig)
    raise SystemExit(1)
text = orig.read_bytes()
# remove UTF-8 BOM if present
if text.startswith(b"\xef\xbb\xbf"):
    text = text[3:]
s = text.decode("utf-8", errors="replace")
lines = s.splitlines()

out_lines = []
for ln in lines:
    t = ln.strip()
    # comment lines that start with $ (PowerShell variables)
    if t.startswith("$"):
        out_lines.append("# [sanitized] " + ln)
        continue
    # comment explicit heredoc markers like @' or @" or ' @ etc.
    if re.search(r"@\'|@\"|\'@|\"@", ln):
        out_lines.append("# [sanitized] " + ln)
        continue
    # comment lines that are a single @ or just a quote+@ or @+quote
    if re.match(r"^\s*[@]['\"]?\s*$", ln) or re.match(r"^\s*['\"]@['\"]?\s*$", ln):
        out_lines.append("# [sanitized] " + ln)
        continue
    # comment common PowerShell cmdlets or pipeline lines
    if re.search(
        r"\b(Copy-Item|Move-Item|Set-Item|Get-Item|Start-Process|New-Item|Set-Alias|Register-ScheduledTask|Import-Module|Get-ChildItem|Remove-Item)\b",
        ln,
    ):
        out_lines.append("# [sanitized] " + ln)
        continue
    # comment lines with PowerShell -operators
    if re.search(r"\s-(replace|like|contains|join|match|split|eq|ne|lt|gt)\b", ln):
        out_lines.append("# [sanitized] " + ln)
        continue
    # comment lines with a standalone ` (backtick) commonly used in PS
    if "`" in ln:
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
    print("PY_COMPILE sanitized5: OK")
except Exception as e:
    print("PY_COMPILE sanitized5: FAILED")
    logger.info(e)
    raise SystemExit(2)
