import json
import pathlib

# Files with UTF-8 BOM issues
files_with_bom = [
    "C:\\EQ12\\data\\file_report_20250919.json",
    "C:\\EQ12\\keys\\credentials.json",
    "C:\\EQ12\\logs\\dnscrypt.json",
    "C:\\EQ12\\openai-python-project\\eq12_godmode_runner\\config.json",
    "C:\\EQ12\\openai-python-project\\eq12_godmode_runner\\dispatcher_config.json",
    "C:\\EQ12\\openai-python-project\\eq12_prompt_runner\\config.json",
    "C:\\EQ12\\openai-python-project\\src\\config.json",
]

# Empty files to fix
empty_files = [
    "C:\\EQ12\\logs\\recycle_report.json",
    "C:\\EQ12\\profiles\\firefox-bot\\notificationstore.json",
]

fixed_count = 0
for file_path in files_with_bom:
    try:
        p = pathlib.Path(file_path)
        if p.exists():
            # Read with BOM, write without BOM
            content = p.read_text(encoding="utf-8-sig")
            # Validate it's valid JSON
            json.loads(content)
            p.write_text(content, encoding="utf-8")
            print(f"Fixed BOM in: {file_path}")
            fixed_count += 1
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")

for file_path in empty_files:
    try:
        p = pathlib.Path(file_path)
        if p.exists() and p.stat().st_size == 0:
            # Write empty JSON object
            p.write_text("{}", encoding="utf-8")
            print(f"Fixed empty file: {file_path}")
            fixed_count += 1
    except Exception as e:
        print(f"Error fixing empty file {file_path}: {e}")

print(f"Total files fixed: {fixed_count}")
