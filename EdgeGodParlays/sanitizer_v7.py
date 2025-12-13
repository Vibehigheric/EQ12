import logging
import re
from pathlib import Path

# Set up logging
logger = logging.getLogger(__name__)

# sanitizer_v7.py - minimal-keep approach: only retain lines that clearly belong to Python code
orig = Path(r"C:/EQ12/EdgeGodParlays/ai_betting_bot_stealth_final_flask_pro.py.merged-candidate.py")
out = orig.with_suffix(".sanitized7.py")
if not orig.exists():
    print("ERROR: original not found", orig)
    raise SystemExit(1)
raw = orig.read_bytes()
if raw.startswith(b"\xef\xbb\xbf"):
    raw = raw[3:]
text = raw.decode("utf-8", errors="replace")
lines = text.splitlines()

keep_patterns = [
    r"^\s*import\b",
    r"^\s*from\b",
    r"^\s*def\b",
    r"^\s*class\b",
    r"^\s*async\b",
    r"^\s*if\b",
    r"^\s*elif\b",
    r"^\s*else\b",
    r"^\s*for\b",
    r"^\s*while\b",
    r"^\s*with\b",
    r"^\s*try\b",
    r"^\s*except\b",
    r"^\s*finally\b",
    r"^\s*return\b",
    r"^\s*print\(",
    r"^\s*#",
    r"^\s*$",
    r"^\s*['\"]{3}",
    r"^\s*[A-Za-z_][A-Za-z0-9_]*\s*=\s*",
]
kp = [re.compile(p) for p in keep_patterns]

out_lines = []
for ln in lines:
    if any(p.match(ln) for p in kp):
        out_lines.append(ln)
    else:
        out_lines.append("# [sanitized] " + ln)

out.write_text("\n".join(out_lines), encoding="utf-8")
print("WROTE:", out)

import py_compile

try:
    py_compile.compile(str(out), doraise=True)
    print("PY_COMPILE sanitized7: OK")
except Exception as e:
    print("PY_COMPILE sanitized7: FAILED")
    logger.info(e)
    raise SystemExit(2)
