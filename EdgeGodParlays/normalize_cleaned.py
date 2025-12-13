import logging
import re
from pathlib import Path

# Set up logging
logger = logging.getLogger(__name__)

# normalize_cleaned.py
# Reads the cleaned candidate produced earlier and normalizes indentation by removing stray indents
# that are not part of a Python block. Writes .cleaned.normalized.py and attempts to py_compile it.
orig = Path(
    r"C:/EQ12/EdgeGodParlays/ai_betting_bot_stealth_final_flask_pro.py.merged-candidate.cleaned.py"
)
out = orig.with_suffix(".cleaned.normalized.py")
if not orig.exists():
    print("ERROR: source cleaned file not found:", orig)
    raise SystemExit(1)
text = orig.read_text(encoding="utf-8", errors="replace")
lines = text.splitlines()

block_stack = []  # stack of indent levels for open blocks
in_triple = False
triple_delim = None

out_lines = []
for ln in lines:
    raw = ln
    stripped = ln.lstrip("\r\n")
    # preserve blank lines
    if stripped.strip() == "":
        out_lines.append("")
        continue
    # preserve triple-quoted strings: detect start/end
    if not in_triple:
        m = re.match(r"^(\s*)([\'\"]{3})", ln)
        if m:
            in_triple = True
            triple_delim = m.group(2)
            out_lines.append(ln)
            continue
    else:
        out_lines.append(ln)
        if triple_delim in ln:
            # end triple
            in_triple = False
            triple_delim = None
        continue
    # If line is a noise comment, strip leading spaces and keep as comment
    if ln.lstrip().startswith("# [noise removed]") or ln.lstrip().startswith("# [sanitized"):
        out_lines.append("# " + ln.lstrip("# ").rstrip())
        continue
    # compute indent
    indent = len(ln) - len(ln.lstrip(" "))
    # pop block stack while current indent <= top
    while block_stack and indent <= block_stack[-1]:
        block_stack.pop()
    # if this line is a block header (ends with ':' ignoring comments) and not a comment
    if re.match(r"^\s*[^#].*:\s*(#.*)?$", ln):
        # keep indentation as-is and push indent to stack
        out_lines.append(ln)
        block_stack.append(indent)
        continue
    # if there is any open block, keep indentation as-is
    if block_stack:
        out_lines.append(ln)
        continue
    # otherwise, strip leading indentation to 0 (top-level)
    out_lines.append(ln.lstrip(" "))

out.write_text("\n".join(out_lines), encoding="utf-8")
print("WROTE:", out)

import py_compile

try:
    py_compile.compile(str(out), doraise=True)
    print("PY_COMPILE normalized: OK")
except Exception as e:
    print("PY_COMPILE normalized: FAILED")
    logger.info(e)
    raise SystemExit(2)
