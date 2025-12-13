from pathlib import Path

path = Path("cfb_dk_boost_optimizer.py")
lines = path.read_text(encoding="utf-8").splitlines()
index = 703 - 1
lines[index] = r'            print(f"\nCSV Export: {csv_path}")'
path.write_text("\n".join(lines) + "\n", encoding="utf-8")
