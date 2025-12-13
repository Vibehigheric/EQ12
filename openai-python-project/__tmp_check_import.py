from pathlib import Path

path = Path("eq12_godmode_runner_plus.py")
text = path.read_text(encoding="utf-8")
old = "import os\nimport json\nimport time\nimport subprocess\nimport threading\nfrom datetime import datetime, timedelta\nfrom pathlib import Path\n\nfrom openai import OpenAI\n\nfrom core.scheduler import export_schedule_summary\nfrom core.state import StateManager, build_state_manager\n\n"
print("found" if old in text else "not found")
