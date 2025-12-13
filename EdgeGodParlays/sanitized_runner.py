import logging
import re
from pathlib import Path

# Set up logging
logger = logging.getLogger(__name__)

# sanitized_runner.py
# Reads a merged-candidate Python file, strips obvious non-Python blocks (PowerShell, heredocs),
# writes a sanitized copy and attempts to py_compile it.

orig = Path(r"C:/EQ12/EdgeGodParlays/ai_betting_bot_stealth_final_flask_pro.py.merged-candidate.py")
sanit = orig.with_suffix(".sanitized.py")

if not orig.exists():
    print("ERROR: original file not found:", orig)
    raise SystemExit(1)

text = orig.read_text(encoding="utf-8", errors="ignore")
lines = text.splitlines()

out_lines = []
skip_block = False
for ln in lines:
    # detect PowerShell variable lines starting with $ (very likely not Python in this context)
    if ln.lstrip().startswith("$"):
        out_lines.append("# [sanitized] " + ln)
        continue
    # detect PowerShell heredoc start @" or @'
    if re.match(r"\s*@\"", ln) or re.match(r"\s*@'", ln):
        skip_block = True
        out_lines.append("# [sanitized] HEREDOC_START")
        continue
    if skip_block:
        # detect heredoc end "@ or '@
        if re.match(r".*\"@\s*$", ln) or re.match(r".*'@\s*$", ln):
            skip_block = False
            out_lines.append("# [sanitized] HEREDOC_END")
        else:
            out_lines.append("# [sanitized] " + ln)
        continue
    # otherwise keep the line
    out_lines.append(ln)

sanit.write_text("\n".join(out_lines), encoding="utf-8")
print("WROTE SANITIZED:", sanit)

# try to compile
import py_compile

try:
    py_compile.compile(str(sanit), doraise=True)
    print("PY_COMPILE on sanitized: OK")
except Exception as e:
    print("PY_COMPILE on sanitized: FAILED")
    logger.info(e)
    raise SystemExit(2)
