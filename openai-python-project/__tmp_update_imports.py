from pathlib import Path

path = Path("eq12_godmode_runner_plus.py")
text = path.read_text(encoding="utf-8")
old = "import os\nimport json\nimport time\nimport subprocess\nimport threading\nfrom datetime import datetime, timedelta\nfrom pathlib import Path\n\nfrom openai import OpenAI\n\nfrom core.scheduler import export_schedule_summary\nfrom core.state import StateManager, build_state_manager\n\n"
new = "import os\nimport json\nimport time\nimport subprocess\nimport threading\nfrom datetime import datetime, timedelta\nfrom pathlib import Path\nfrom typing import Any, Dict, List\n\nfrom openai import OpenAI\n\nfrom core.scheduler import export_schedule_summary\nfrom core.state import StateManager, build_state_manager\nfrom integrations.console import build_console\nfrom integrations.database import build_database\nfrom integrations.drive_client import build_drive_connector\nfrom integrations.email_client import build_email_executor\nfrom integrations.pdf_digest import build_digest_builder\n\n"
if old not in text:
    raise SystemExit("import block not found for replacement")
text = text.replace(old, new, 1)
path.write_text(text, encoding="utf-8")
