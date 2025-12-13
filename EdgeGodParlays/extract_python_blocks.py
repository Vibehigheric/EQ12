import logging
import re
from pathlib import Path

# Set up logging
logger = logging.getLogger(__name__)

# extract_python_blocks.py
# Scans a mixed file and extracts contiguous Python-like blocks (imports, defs, classes, top-level assignments)
# Writes an output file with a header and the extracted blocks: *.extracted.py
orig = Path(r"C:/EQ12/EdgeGodParlays/ai_betting_bot_stealth_final_flask_pro.py.merged-candidate.py")
out = orig.with_suffix(".extracted.py")
if not orig.exists():
    print("ERROR: original not found", orig)
    raise SystemExit(1)
text = orig.read_text(encoding="utf-8", errors="replace")
lines = text.splitlines()

start_patterns = [
    re.compile(p)
    for p in [
        r"^\s*import\b",
        r"^\s*from\b",
        r"^\s*def\b",
        r"^\s*class\b",
        r"^\s*async\b",
        r"^\s*[A-Za-z_][A-Za-z0-9_]*\s*=\s*",
    ]
]

out_lines = [
    "# extracted Python blocks from merged-candidate\n# Source: ai_betting_bot_stealth_final_flask_pro.py.merged-candidate.py\n"
]

i = 0
n = len(lines)
while i < n:
    ln = lines[i]
    matched = any(p.match(ln) for p in start_patterns)
    if matched:
        # start a block
        out_lines.append("\n")
        # append the starting line
        out_lines.append(ln)
        i += 1
        # append subsequent indented lines (body)
        while i < n and (
            lines[i].startswith("    ") or lines[i].startswith("\t") or lines[i].strip() == ""
        ):
            out_lines.append(lines[i])
            i += 1
        # block ended
        continue
    else:
        i += 1

# write output
out.write_text("\n".join(out_lines), encoding="utf-8")
print("WROTE:", out)

# try compile
import py_compile

try:
    py_compile.compile(str(out), doraise=True)
    print("PY_COMPILE extracted: OK")
except Exception as e:
    print("PY_COMPILE extracted: FAILED")
    logger.info(e)
    raise SystemExit(2)
