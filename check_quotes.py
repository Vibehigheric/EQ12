from pathlib import Path

text = Path("cfb_dk_boost_optimizer.py").read_text(encoding="utf-8")
for i, line in enumerate(text.splitlines(), 1):
    if '\\"' in line:
        print(i, line.encode("unicode_escape").decode())
