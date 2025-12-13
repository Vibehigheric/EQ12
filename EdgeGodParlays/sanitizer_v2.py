import logging
import re
from pathlib import Path

# Set up logging
logger = logging.getLogger(__name__)

# stricter sanitizer: produce .sanitized2.py
orig = Path(r"C:/EQ12/EdgeGodParlays/ai_betting_bot_stealth_final_flask_pro.py.merged-candidate.py")
out = orig.with_suffix(".sanitized2.py")
if not orig.exists():
    print("ERROR: original not found", orig)
    raise SystemExit(1)
text = orig.read_text(encoding="utf-8", errors="replace")
lines = text.splitlines()

out_lines = []
for ln in lines:
    s = ln.strip()
    # comment PowerShell variable lines
    if ln.lstrip().startswith("$"):
        out_lines.append("# [sanitized] " + ln)
        continue
    # comment lines that are just @ markers or close heredoc markers
    if s in ("@", "@'", '@"', "'@", '"@'):
        out_lines.append("# [sanitized] " + ln)
        continue
    if re.match(r"^@['\"]", s) or re.match(r"^['\"]@", s):
        out_lines.append("# [sanitized] " + ln)
        continue
    # comment lines with PowerShell replace operator -replace or -like etc
    if re.search(r"\s-replace\s|\s-join\s|\s-contains\s|\s-lt\s|\s-gt\s", ln):
        out_lines.append("# [sanitized] " + ln)
        continue
    # comment lines with backticks (PowerShell style or markdown code)
    if "`" in ln and not (ln.strip().startswith("`") and ln.strip().endswith("`")):
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
    print("PY_COMPILE sanitized2: OK")
except Exception as e:
    print("PY_COMPILE sanitized2: FAILED")
    logger.info(e)
    raise SystemExit(2)
