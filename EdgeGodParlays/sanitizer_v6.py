import logging
import re
from pathlib import Path

# Set up logging
logger = logging.getLogger(__name__)

# sanitizer_v6.py - conservative Python-preserving sanitizer
# Keeps lines that look like Python (imports, def/class, control statements, assignments, comments, docstrings)
# Comments out any line that appears non-Python (PowerShell/other artifacts).
orig = Path(r"C:/EQ12/EdgeGodParlays/ai_betting_bot_stealth_final_flask_pro.py.merged-candidate.py")
out = orig.with_suffix(".sanitized6.py")
if not orig.exists():
    print("ERROR: original not found", orig)
    raise SystemExit(1)
text = orig.read_bytes()
# remove BOM if present
if text.startswith(b"\xef\xbb\xbf"):
    text = text[3:]
s = text.decode("utf-8", errors="replace")
lines = s.splitlines()

py_start = re.compile(
    r"^\s*(import\b|from\b|def\b|class\b|async\b|@|if\b|elif\b|else\b|for\b|while\b|with\b|try\b|except\b|finally\b|return\b|yield\b|pass\b|raise\b|assert\b|print\(|\"\"\"|\'\'\')"
)
assign_like = re.compile(r"^\s*[A-Za-z_][A-Za-z0-9_]*\s*=")
comment = re.compile(r"^\s*#")

out_lines = []
for ln in lines:
    if (
        py_start.match(ln)
        or assign_like.match(ln)
        or comment.match(ln)
        or ln.strip() == ""
        or ln.strip().startswith(('"""', "'''"))
    ):
        out_lines.append(ln)
    else:
        out_lines.append("# [sanitized] " + ln)

out.write_text("\n".join(out_lines), encoding="utf-8")
print("WROTE:", out)

import py_compile

try:
    py_compile.compile(str(out), doraise=True)
    print("PY_COMPILE sanitized6: OK")
except Exception as e:
    print("PY_COMPILE sanitized6: FAILED")
    logger.info(e)
    raise SystemExit(2)
