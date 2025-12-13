from pathlib import Path

lines = Path("cfb_dk_boost_optimizer.py").read_text(encoding="utf-8").splitlines()
for i, line in enumerate(lines):
    if "CSV Export: {csv_path}" in line:
        print(i)
