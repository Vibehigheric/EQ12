import re
from pathlib import Path

# fix_unclosed_parens.py
# Rewrites a sanitized normalized Python file to replace unclosed parenthesis assignments
# like `prompt = (` or `guard = (` whose bodies were commented out, converting them to
# a safe single-line assignment: prompt = "" (preserving indentation).

src = Path(
    r"C:/EQ12/EdgeGodParlays/ai_betting_bot_stealth_final_flask_pro.py.merged-candidate.cleaned.cleaned.normalized.py"
)
out = src.with_suffix(".fixed.py")
if not src.exists():
    print("ERROR: source not found", src)
    raise SystemExit(1)
lines = src.read_text(encoding="utf-8", errors="replace").splitlines()

pattern = re.compile(r"^(?P<indent>\s*)(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*\($")

i = 0
n = len(lines)
out_lines = []
while i < n:
    m = pattern.match(lines[i])
    if m:
        indent = m.group("indent")
        name = m.group("name")
        # scan forward until a non-comment non-empty line or until a close paren is found
        j = i + 1
        found_close = False
        while j < n:
            line = lines[j]
            stripped = line.strip()
            # if we find a closing paren on a non-comment line, consider it closed
            if stripped == ")" or stripped.endswith(")") and not stripped.startswith("#"):
                found_close = True
                break
            # if we find a line that's not a comment or blank, we treat as broken and will replace whole block
            if not (stripped.startswith("#") or stripped == ""):
                break
            j += 1
        # replace the entire block i..j-1 with a safe assignment
        out_lines.append(f'{indent}{name} = ""  # [fixed: removed commented block]\n')
        i = j
        continue
    else:
        out_lines.append(lines[i])
        i += 1

out.write_text("\n".join(out_lines), encoding="utf-8")
print("WROTE fixed file to", out)

# attempt compile
import py_compile

try:
    py_compile.compile(str(out), doraise=True)
    print("PY_COMPILE fixed: OK")
except Exception:
    print("PY_COMPILE fixed: FAILED")
    import traceback

    traceback.print_exc()
    raise SystemExit(2)
