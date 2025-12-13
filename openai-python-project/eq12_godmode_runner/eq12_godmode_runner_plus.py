import json
import logging
import os
import subprocess
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from openai import OpenAI

# Set up logging
logger = logging.getLogger(__name__)


try:
    from openai import AuthenticationError  # type: ignore
except ImportError:  # pragma: no cover - fallback for legacy clients

    class AuthenticationError(Exception):  # type: ignore
        """Fallback when AuthenticationError is unavailable."""

        pass


from core.scheduler import export_schedule_summary
from core.state import StateManager, build_state_manager
from eq12_shared import CredentialError, CredentialManager

# === Optional: colored terminal output ===
try:
    from colorama import Fore, Style, init

    init(autoreset=True)
    COLORS_AVAILABLE = True
except ImportError:

    class Dummy:
        def __getattr__(self, name) -> bool:
            return ""

    Fore = Style = Dummy()
    COLORS_AVAILABLE = False

# === Credential Manager ===
credential_manager = CredentialManager()
_CLIENT_LOCK = threading.Lock()
_CLIENT: OpenAI | None = None


def get_openai_client(force_refresh: bool = False) -> OpenAI:
    """Return a cached OpenAI client backed by the shared credential store."""
    global _CLIENT
    with _CLIENT_LOCK:
        if force_refresh or _CLIENT is None:
            api_key = credential_manager.ensure_env(
                "openai.api_key",
                "OPENAI_API_KEY",
                prompt="Enter your OpenAI API key for EQ12 AI Ops Commander: ",
            )
            _CLIENT = OpenAI(api_key=api_key)
    return _CLIENT


def should_retry_openai_error(error: Exception, attempt: int) -> bool:
    """Prompt for a new API key when authentication fails."""
    unauthorized_codes = {401, 403}
    status = getattr(error, "status_code", None)
    if isinstance(error, AuthenticationError) or status in unauthorized_codes:
        if attempt >= 2:
            return False
        credential_manager.invalidate(
            "openai.api_key",
            prompt="OpenAI rejected the API key. Enter a new key: ",
        )
        get_openai_client(force_refresh=True)
        return True
    return False


BASE_DIR = Path(__file__).resolve().parent
STATE_MANAGER: StateManager = build_state_manager(BASE_DIR)
INTEGRATIONS_CACHE: dict[str, Any] = {}

# === Windows Task Scheduler XML Template ===
TASK_TEMPLATE = """<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>{start_boundary}</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByDay>
        <DaysInterval>{days_interval}</DaysInterval>
      </ScheduleByDay>
    </CalendarTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>S-1-5-32-545</UserId>
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>true</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT2H</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>{python_path}</Command>
      <Arguments>"{script_path}" --module {module} --scheduled</Arguments>
      <WorkingDirectory>{working_dir}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>"""

# === Default Schedule Templates ===
DEFAULT_SCHEDULES = {
    "daily": {
        "sports_morning": {
            "module": "sports",
            "time": "07:00",
            "description": "Morning sports analysis and betting optimization",
        },
        "travel_midday": {
            "module": "travel",
            "time": "12:00",
            "description": "Travel deals and flight monitoring",
        },
        "housing_midday": {
            "module": "housing",
            "time": "12:30",
            "description": "Real estate market tracking",
        },
        "study_evening": {
            "module": "study",
            "time": "18:00",
            "description": "Learning and certification progress",
        },
        "sports_recap": {
            "module": "sports",
            "time": "19:00",
            "description": "Sports results analysis and next-day prep",
        },
    },
    "weekly": {
        "executive_digest": {
            "module": "chain",
            "time": "MON:08:00",
            "description": "Weekly executive summary (Sports+Housing+Civil Service)",
            "modules": ["sports", "housing", "civil_service"],
        },
        "dropship_sync": {
            "module": "dropship",
            "time": "WED:12:00",
            "description": "Dropshipping product sync and SEO optimization",
        },
        "affiliate_content": {
            "module": "chain",
            "time": "FRI:18:00",
            "description": "Content generation for affiliate marketing",
            "modules": ["travel", "dropship"],
        },
        "commander_review": {
            "module": "chain",
            "time": "SUN:20:00",
            "description": "Full system review and strategic planning",
            "modules": [
                "sports",
                "travel",
                "housing",
                "dropship",
                "civil_service",
                "study",
            ],
        },
    },
}


# === Scheduling Functions ===
def get_python_executable() -> bool:
    """Get the current Python executable path"""
    import sys

    return sys.executable


def schedule_task(module, start_time="07:00", daily=True, description="") -> bool:
    """Create and register a Windows Task Scheduler task"""
    try:
        # Parse time
        if ":" in start_time and len(start_time.split(":")) == 2:
            hour, minute = start_time.split(":")
        else:
            print(
                Fore.RED
                + f"❌ Invalid time format: {start_time}. Use HH:MM format."
                + Style.RESET_ALL
            )
            return False

        # Calculate start boundary (tomorrow at specified time)
        now = datetime.now()
        start_date = now.replace(hour=int(hour), minute=int(minute), second=0, microsecond=0)
        if start_date <= now:
            start_date += timedelta(days=1)

        start_boundary = start_date.strftime("%Y-%m-%dT%H:%M:%S")
        days_interval = 1 if daily else 7

        # Get paths
        python_path = get_python_executable()
        script_path = os.path.abspath(__file__)
        working_dir = os.path.dirname(script_path)

        # Generate XML content
        xml_content = TASK_TEMPLATE.format(
            start_boundary=start_boundary,
            days_interval=days_interval,
            python_path=python_path,
            script_path=script_path,
            module=module,
            working_dir=working_dir,
        )

        # Create XML file
        task_name = f"EQ12_{module}_{'Daily' if daily else 'Weekly'}"
        xml_filename = f"{task_name}.xml"
        xml_path = os.path.join(working_dir, xml_filename)

        with open(xml_path, "w", encoding="utf-16") as f:
            f.write(xml_content)

        print(Fore.BLUE + f"📄 Created task XML: {xml_filename}" + Style.RESET_ALL)

        # Register with Windows Task Scheduler
        try:
            result = subprocess.run(
                ["schtasks", "/create", "/tn", task_name, "/xml", xml_path, "/f"],
                capture_output=True,
                text=True,
                check=True,
            )

            print(Fore.GREEN + f"✅ Task '{task_name}' registered successfully!" + Style.RESET_ALL)
            print(
                Fore.CYAN
                + f"   Next run: {start_boundary} ({'daily' if daily else 'weekly'})"
                + Style.RESET_ALL
            )
            if description:
                print(Fore.WHITE + f"   Purpose: {description}" + Style.RESET_ALL)

            # Clean up XML file
            os.remove(xml_path)
            return True

        except subprocess.CalledProcessError as e:
            print(Fore.RED + f"❌ Failed to register task: {e.stderr}" + Style.RESET_ALL)
            print(
                Fore.YELLOW
                + "💡 Try running as Administrator or check Windows Task Scheduler manually"
                + Style.RESET_ALL
            )
            return False

    except Exception as e:
        print(Fore.RED + f"❌ Error creating scheduled task: {e}" + Style.RESET_ALL)
        return False


def setup_default_schedules() -> bool:
    """Set up all default daily and weekly schedules"""
    print(
        Fore.CYAN + "\n🗓️  Setting up default EQ12 AI Ops Commander schedules..." + Style.RESET_ALL
    )

    success_count = 0
    total_count = 0

    # Daily schedules
    print(Fore.BLUE + "\n📅 Daily Schedules:" + Style.RESET_ALL)
    for schedule_name, config in DEFAULT_SCHEDULES["daily"].items():
        total_count += 1
        print(f"   Setting up {schedule_name}...")
        if schedule_task(config["module"], config["time"], True, config["description"]):
            success_count += 1
        time.sleep(0.5)  # Small delay between task creation

    # Weekly schedules
    print(Fore.BLUE + "\n📊 Weekly Schedules:" + Style.RESET_ALL)
    for schedule_name, config in DEFAULT_SCHEDULES["weekly"].items():
        total_count += 1
        print(f"   Setting up {schedule_name}...")
        # Parse weekly time format (MON:08:00)
        day_time = config["time"]
        if ":" in day_time:
            time_part = day_time.split(":", 1)[1] if ":" in day_time else "08:00"
        else:
            time_part = "08:00"

        if schedule_task(config["module"], time_part, False, config["description"]):
            success_count += 1
        time.sleep(0.5)

    print(
        Fore.GREEN
        + f"\n✅ Setup complete! {success_count}/{total_count} schedules registered"
        + Style.RESET_ALL
    )

    if success_count == total_count:
        print(
            Fore.CYAN
            + "🚀 Your EQ12 AI Ops Commander is now running on autopilot!"
            + Style.RESET_ALL
        )
        print(
            Fore.WHITE
            + "   • Daily: Sports (7AM), Travel (12PM), Housing (12:30PM), Study (6PM), Sports Recap (7PM)"
            + Style.RESET_ALL
        )
        print(
            Fore.WHITE
            + "   • Weekly: Executive Digest (Mon), Dropship Sync (Wed), Content Gen (Fri), Commander Review (Sun)"
            + Style.RESET_ALL
        )
    else:
        print(
            Fore.YELLOW
            + "⚠️  Some tasks failed to register. Check Windows Task Scheduler or run as Administrator."
            + Style.RESET_ALL
        )


def list_scheduled_tasks() -> bool:
    """List all EQ12 scheduled tasks"""
    try:
        result = subprocess.run(
            ["schtasks", "/query", "/fo", "csv", "/nh"],
            capture_output=True,
            text=True,
            check=True,
        )

        lines = result.stdout.strip().split("\n")
        eq12_tasks = []

        for line in lines:
            if "EQ12_" in line:
                parts = line.split(",")
                if len(parts) >= 2:
                    task_name = parts[0].strip('"')
                    status = parts[1].strip('"')
                    eq12_tasks.append((task_name, status))

        if eq12_tasks:
            print(Fore.CYAN + "\n📋 Current EQ12 Scheduled Tasks:" + Style.RESET_ALL)
            for task_name, status in eq12_tasks:
                status_color = Fore.GREEN if status == "Ready" else Fore.YELLOW
                print(f"   {status_color}{task_name}{Style.RESET_ALL} - {status}")
        else:
            print(Fore.YELLOW + "\n📋 No EQ12 scheduled tasks found" + Style.RESET_ALL)

    except subprocess.CalledProcessError as e:
        print(Fore.RED + f"❌ Error listing tasks: {e}" + Style.RESET_ALL)


def remove_scheduled_task(task_name) -> bool:
    """Remove a specific scheduled task"""
    try:
        result = subprocess.run(
            ["schtasks", "/delete", "/tn", task_name, "/f"],
            capture_output=True,
            text=True,
            check=True,
        )

        print(Fore.GREEN + f"✅ Task '{task_name}' removed successfully" + Style.RESET_ALL)
        return True

    except subprocess.CalledProcessError as e:
        print(Fore.RED + f"❌ Failed to remove task '{task_name}': {e.stderr}" + Style.RESET_ALL)
        return False


# === Prompt modules ===
MODULES = {
    "1": "sports",
    "2": "travel",
    "3": "dropship",
    "4": "housing",
    "5": "civil_service",
    "6": "study",
    "0": "custom",
}


# === Load stored prompt ===
def load_prompt(module_name: str) -> str:
    if module_name == "custom":
        return input(Fore.YELLOW + "\nType your custom prompt:\n> " + Style.RESET_ALL)
    path = os.path.join(os.path.dirname(__file__), "prompts", f"{module_name}.txt")
    if not os.path.exists(path):
        raise FileNotFoundError(f"No prompt file found for {module_name}")
    with open(path, encoding="utf-8") as f:
        return f.read()


# === Run GPT-5 with Pro reasoning ===
def run_prompt(prompt: str, module: str = "Unknown", *, attempt: int = 1) -> str:
    start = time.time()
    print(Fore.BLUE + f"🤖 Running {module.title()} with GPT-5 Pro Reasoning..." + Style.RESET_ALL)

    try:
        client = get_openai_client()
        resp = client.chat.completions.create(
            model="gpt-5",
            messages=[
                {
                    "role": "system",
                    "content": "You are EQ12 GOD MODE COMMANDER++: automate, analyze, and create with maximum depth.",
                },
                {"role": "user", "content": prompt},
            ],
            reasoning={"effort": "heavy"},
            max_tokens=3000,
        )
        elapsed = time.time() - start
        content = resp.choices[0].message.content
        print(
            Fore.GREEN
            + f"\n=== {module.title()} Response (took {elapsed:.2f}s) ===\n"
            + Style.RESET_ALL
        )
        return content
    except CredentialError as err:
        print(Fore.RED + f"Credential error: {err}" + Style.RESET_ALL)
        return f"Credential error: {err}"
    except Exception as e:
        if should_retry_openai_error(e, attempt):
            return run_prompt(prompt, module, attempt=attempt + 1)
        print(Fore.RED + f"Error: {e}" + Style.RESET_ALL)
        return f"Error occurred: {e}"


# === Generate executive summary from chained outputs ===
def generate_executive_summary(chain_outputs: list) -> str:
    print(Fore.CYAN + "\n🎯 Generating Executive Summary..." + Style.RESET_ALL)

    combined_content = "\n\n".join(
        [f"MODULE: {output['module'].upper()}\n{output['content']}" for output in chain_outputs]
    )

    summary_prompt = f"""
You are the EQ12 GOD MODE COMMANDER++. Analyze these multiple automation outputs and create:

1. EXECUTIVE SUMMARY (2-3 sentences)
2. KEY INSIGHTS (top 3 cross-module patterns)
3. PRIORITY ACTIONS (next 5 concrete steps)
4. SYNERGY OPPORTUNITIES (how modules can work together)

CHAIN OUTPUTS TO ANALYZE:
{combined_content}

Be strategic, actionable, and identify connections between modules.
"""

    return run_prompt(summary_prompt, "Executive Summary")


# === Generate JSON Action Plan ===
def generate_json_action_plan(chain_outputs: list) -> str:
    print(Fore.CYAN + "\n📋 Generating JSON Action Plan..." + Style.RESET_ALL)

    combined_content = "\n\n".join(
        [f"MODULE: {output['module'].upper()}\n{output['content']}" for output in chain_outputs]
    )

    json_prompt = f"""
You are EQ12 GOD MODE COMMANDER++ creating a structured action plan for automation systems.

TASK: Analyze the module outputs and create a JSON action plan with this EXACT structure:

{{
  "urgent": [
    "specific urgent action that needs immediate attention",
    "another urgent task with clear action items"
  ],
  "short_term": [
    "short-term action for next 1-7 days",
    "another short-term task with specific deliverable"
  ],
  "long_term": [
    "long-term strategic action for 1-6 months",
    "another long-term planning item"
  ],
  "automation_opportunities": [
    "process that can be automated using available tools",
    "another automation opportunity with clear benefits"
  ],
  "success_metrics": [
    "measurable KPI to track progress",
    "another metric to monitor success"
  ],
  "cross_module_synergies": [
    "how modules can work together for better results"
  ]
}}

MODULES ANALYZED: {len([o for o in chain_outputs if o['module'] != 'executive_summary'])} modules

RAW OUTPUT DATA:
{combined_content}

CRITICAL INSTRUCTIONS:
- Return ONLY the JSON structure, no additional text
- Ensure all JSON is valid and properly formatted
- Include at least 2-3 items in each category
- Make tasks specific and actionable
- Use clear, concise language
"""
    return run_prompt(json_prompt, "JSON Action Plan")


# === Save output to logs ===
def save_log(module: str, output: str) -> bool:
    logs_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(logs_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{module}_{timestamp}.txt" if module != "custom" else f"custom_{timestamp}.txt"

    with open(os.path.join(logs_dir, filename), "w", encoding="utf-8") as f:
        f.write("=== EQ12 GOD MODE COMMANDER++ LOG ===\n")
        f.write(f"Module: {module.title()}\n")
        f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"{'='*50}\n\n")
        f.write(output)

    # Also save as "last" version for quick access
    last_filename = f"{module}_last.txt"
    with open(os.path.join(logs_dir, last_filename), "w", encoding="utf-8") as f:
        f.write(output)

    print(Fore.MAGENTA + f"📁 [Saved to logs/{filename}]" + Style.RESET_ALL)


# === Save chained output to logs ===
def save_chain_log(chain_outputs: list, timestamp: str) -> bool:
    logs_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(logs_dir, exist_ok=True)

    chain_filename = f"chain_{timestamp}.txt"
    chain_path = os.path.join(logs_dir, chain_filename)

    with open(chain_path, "w", encoding="utf-8") as f:
        f.write("=== EQ12 GOD MODE COMMANDER++ - CHAIN EXECUTION LOG ===\n")
        f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(
            f"Modules Executed: {len([o for o in chain_outputs if o['module'] not in ['executive_summary', 'json_action_plan', 'smart_dispatch_results']])}\n"
        )
        f.write("=" * 80 + "\n\n")

        for output in chain_outputs:
            module_name = output["module"].replace("_", " ").title()
            f.write(f"\n{'='*20} {module_name.upper()} {'='*20}\n")
            f.write(output["content"])
            f.write(f"\n{'='*60}\n")

    print(Fore.CYAN + f"📊 [Chain log saved to logs/{chain_filename}]" + Style.RESET_ALL)


# === Validate and save JSON ===
def save_json_action_plan(json_content: str, timestamp: str) -> bool:
    try:
        import re

        logs_dir = Path(__file__).resolve().parent / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)

        json_match = re.search(r"\{.*\}", json_content, re.DOTALL)
        if json_match:
            clean_json = json_match.group()
            parsed = json.loads(clean_json)

            json_path = logs_dir / f"action_plan_{timestamp}.json"
            json_path.write_text(json.dumps(parsed, indent=2, ensure_ascii=False), encoding="utf-8")

            print(Fore.CYAN + f"[saved] logs/{json_path.name}" + Style.RESET_ALL)
            return json_path
        print(Fore.RED + "[error] Could not extract valid JSON from response" + Style.RESET_ALL)
        debug_path = logs_dir / f"action_plan_debug_{timestamp}.txt"
        debug_path.write_text(json_content, encoding="utf-8")
        print(Fore.YELLOW + f"[saved] logs/{debug_path.name} (raw response)" + Style.RESET_ALL)
        return None

    except json.JSONDecodeError as e:
        print(Fore.RED + f"[error] JSON validation failed: {e}" + Style.RESET_ALL)
        return None
    except Exception as e:
        print(Fore.RED + f"[error] Error saving JSON: {e}" + Style.RESET_ALL)
        return None


# === Load configuration ===
def load_config() -> bool:
    """Load configuration from config.json"""
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    if not os.path.exists(config_path):
        return {"dispatch": {"auto_execute": False}}

    with open(config_path) as f:
        return json.load(f)


# === Show colorful banner ===
def show_banner() -> bool:
    banner = """
╔═══════════════════════════════════════════════╗
║     EQ12 AI OPS COMMANDER++ 🤖🚀              ║
║  GPT-5 + Smart Dispatch + Auto-Scheduler      ║
║     Intelligence ⚡ Automation ⚡ Execution     ║
╚═══════════════════════════════════════════════╝
"""
    logger.info(Fore.CYAN + banner + Style.RESET_ALL)

    # Check for existing scheduled tasks
    try:
        result = subprocess.run(
            ["schtasks", "/query", "/fo", "csv", "/nh"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        eq12_tasks = [line for line in result.stdout.split("\n") if "EQ12_" in line]

        if eq12_tasks:
            print(
                Fore.GREEN
                + f"🗓️  AI Ops Status: {len(eq12_tasks)} automated tasks running"
                + Style.RESET_ALL
            )
        else:
            print(
                Fore.YELLOW
                + "🗓️  AI Ops Status: No scheduled automation (use [auto] to setup)"
                + Style.RESET_ALL
            )

    except:
        pass  # Silently continue if can't check tasks

    if not COLORS_AVAILABLE:
        print(
            Fore.YELLOW
            + "💡 Tip: Install colorama for enhanced colors: pip install colorama"
            + Style.RESET_ALL
        )


def main() -> bool:
    show_banner()

    while True:
        print(Fore.CYAN + "\n=== EQ12 AI OPS COMMANDER++ ===" + Style.RESET_ALL)

        # Single module options
        for k, v in MODULES.items():
            icon = "✨" if k == "0" else "🔥"
            display_name = "Custom Prompt" if v == "custom" else v.replace("_", " ").title()
            print(f"{Fore.WHITE}[{k}]{Style.RESET_ALL} {icon} {display_name}")

        # Enhanced mode options
        print(f"{Fore.YELLOW}[m]{Style.RESET_ALL} ⚡ Multi-Chain Mode (run multiple modules)")
        print(f"{Fore.CYAN}[s]{Style.RESET_ALL} 🎯 Smart Dispatch Test (test auto-execution)")
        print(f"{Fore.GREEN}[c]{Style.RESET_ALL} ⚙️  Configuration (view/edit settings)")

        # Scheduling options
        print(f"{Fore.MAGENTA}[schedule]{Style.RESET_ALL} 🗓️  Schedule Tasks (AI Ops Commander)")
        print(f"{Fore.BLUE}[auto]{Style.RESET_ALL} 🚀 Setup Default Schedules (Full Automation)")
        print(f"{Fore.WHITE}[tasks]{Style.RESET_ALL} 📋 Manage Scheduled Tasks")

        print(f"{Fore.RED}[q]{Style.RESET_ALL} 🚪 Quit")

        choice = input(Fore.YELLOW + "\nSelect option: " + Style.RESET_ALL).strip()

        if choice.lower() in ["q", "quit", "exit"]:
            print(
                Fore.MAGENTA + "\n👋 Exiting EQ12 God Mode Commander++. Goodbye!" + Style.RESET_ALL
            )
            break

        # === CHAIN MODE (COMMANDER++ EDITION) ===
        if choice.lower() == "m":
            print(Fore.CYAN + "\n⚡ COMMANDER++ CHAIN MODE ACTIVATED ⚡" + Style.RESET_ALL)
            print("Available modules:")
            for k, v in MODULES.items():
                if k != "0":  # Exclude custom for chain mode
                    print(f"  [{k}] {v.replace('_', ' ').title()}")

            selection = input(
                Fore.YELLOW
                + "\nEnter module numbers (comma-separated, e.g. 1,2,4): "
                + Style.RESET_ALL
            )
            selected_keys = [
                x.strip() for x in selection.split(",") if x.strip() in MODULES and x.strip() != "0"
            ]

            if not selected_keys:
                print(Fore.RED + "❌ No valid modules selected." + Style.RESET_ALL)
                continue

            selected_modules = [MODULES[key] for key in selected_keys]
            print(
                Fore.GREEN
                + f"🎯 Chain selected: {' → '.join([m.title() for m in selected_modules])}"
                + Style.RESET_ALL
            )

            # Execute chain
            chain_outputs = []
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            for i, module in enumerate(selected_modules, 1):
                print(
                    Fore.BLUE
                    + f"\n📍 Step {i}/{len(selected_modules)}: {module.title()}"
                    + Style.RESET_ALL
                )
                try:
                    prompt = load_prompt(module)
                    output = run_prompt(prompt, module)
                    logger.info(output)

                    chain_outputs.append({"module": module, "content": output})

                    print(Fore.MAGENTA + f"✅ {module.title()} completed" + Style.RESET_ALL)

                except Exception as e:
                    print(Fore.RED + f"❌ Error in {module}: {e}" + Style.RESET_ALL)
                    chain_outputs.append({"module": module, "content": f"Error: {e}"})

            # Generate executive summary and JSON action plan
            if len(chain_outputs) > 1:
                try:
                    # Executive Summary
                    summary = generate_executive_summary(chain_outputs)
                    logger.info(summary)
                    chain_outputs.append({"module": "executive_summary", "content": summary})

                    # JSON Action Plan
                    json_plan = generate_json_action_plan(
                        chain_outputs[:-1]
                    )  # Exclude summary from JSON generation
                    print(Fore.YELLOW + "\n📋 JSON ACTION PLAN GENERATED" + Style.RESET_ALL)

                    # Display formatted JSON preview
                    try:
                        import re

                        json_match = re.search(r"\{.*\}", json_plan, re.DOTALL)
                        if json_match:
                            parsed_json = json.loads(json_match.group())
                            print(Fore.WHITE + "\nACTION PLAN PREVIEW:" + Style.RESET_ALL)
                            print(
                                Fore.GREEN
                                + f"• Urgent Tasks: {len(parsed_json.get('urgent', []))}"
                                + Style.RESET_ALL
                            )
                            print(
                                Fore.BLUE
                                + f"• Short-term Tasks: {len(parsed_json.get('short_term', []))}"
                                + Style.RESET_ALL
                            )
                            print(
                                Fore.MAGENTA
                                + f"• Long-term Tasks: {len(parsed_json.get('long_term', []))}"
                                + Style.RESET_ALL
                            )
                            print(
                                Fore.CYAN
                                + f"• Automation Opportunities: {len(parsed_json.get('automation_opportunities', []))}"
                                + Style.RESET_ALL
                            )

                            try:
                                state_records = STATE_MANAGER.reconcile_plan(parsed_json)
                                if state_records:
                                    print(
                                        Fore.CYAN
                                        + f"\nState tracker updated: {len(state_records)} tasks queued"
                                        + Style.RESET_ALL
                                    )
                            except Exception as state_error:
                                print(
                                    Fore.RED
                                    + f"\nState tracking error: {state_error}"
                                    + Style.RESET_ALL
                                )

                            try:
                                schedule_summary_path = export_schedule_summary(
                                    parsed_json, BASE_DIR
                                )
                                print(
                                    Fore.YELLOW
                                    + f"\nScheduler artifacts written to {schedule_summary_path.as_posix()}"
                                    + Style.RESET_ALL
                                )
                            except Exception as schedule_error:
                                print(
                                    Fore.RED
                                    + f"\nScheduler generation error: {schedule_error}"
                                    + Style.RESET_ALL
                                )

                            # COMMANDER++ SMART AUTO-DISPATCH
                            try:
                                from executors.dispatcher import dispatch_plan

                                config = load_config()
                                if config.get("dispatch", {}).get("auto_execute", True):
                                    print(
                                        Fore.CYAN
                                        + "\n🤖 SMART DISPATCH SYSTEM ENGAGING..."
                                        + Style.RESET_ALL
                                    )

                                    # Dispatch actions intelligently
                                    dispatch_results = dispatch_plan(parsed_json)

                                    for priority_key in (
                                        "urgent",
                                        "short_term",
                                        "long_term",
                                    ):
                                        for result in dispatch_results.get(priority_key, []):
                                            action_text = result.get("action")
                                            status = (
                                                "completed"
                                                if result.get("success", True)
                                                else "failed"
                                            )
                                            if action_text:
                                                STATE_MANAGER.update_task_by_text(
                                                    action_text,
                                                    status,
                                                    {"dispatch": result},
                                                )
                                            log_action = action_text or str(
                                                result.get("plan_item", priority_key)
                                            )
                                            STATE_MANAGER.log_execution(
                                                log_action, priority_key, result
                                            )

                                    snapshot = STATE_MANAGER.snapshot()
                                    for priority_key in (
                                        "urgent",
                                        "short_term",
                                        "long_term",
                                    ):
                                        tasks = snapshot.get("tasks", {}).get(priority_key, [])
                                        total = len(tasks)
                                        completed = sum(
                                            1 for task in tasks if task.get("status") == "completed"
                                        )
                                        failed = sum(
                                            1 for task in tasks if task.get("status") == "failed"
                                        )
                                        pending = total - completed - failed
                                        print(
                                            Fore.WHITE
                                            + f"State {priority_key}: {completed} completed / {failed} failed / {pending} pending"
                                            + Style.RESET_ALL
                                        )

                                    # Save dispatch results
                                    chain_outputs.append(
                                        {
                                            "module": "smart_dispatch_results",
                                            "content": json.dumps(dispatch_results, indent=2),
                                        }
                                    )

                                    print(
                                        Fore.GREEN
                                        + "✅ Smart dispatch completed!"
                                        + Style.RESET_ALL
                                    )

                                else:
                                    print(
                                        Fore.YELLOW
                                        + "\n💡 Smart dispatch disabled. Enable in config.json to auto-execute actions."
                                        + Style.RESET_ALL
                                    )

                            except ImportError as e:
                                print(
                                    Fore.RED
                                    + f"❌ Smart dispatcher not available: {e}"
                                    + Style.RESET_ALL
                                )
                                print(
                                    Fore.YELLOW
                                    + "💡 Install missing dependencies or check executor modules."
                                    + Style.RESET_ALL
                                )
                            except Exception as e:
                                print(Fore.RED + f"❌ Smart dispatch error: {e}" + Style.RESET_ALL)

                    except Exception as e:
                        print(Fore.RED + f"❌ JSON parsing error: {e}" + Style.RESET_ALL)
                        print(Fore.WHITE + json_plan[:300] + "..." + Style.RESET_ALL)

                    # Save JSON action plan
                    save_json_action_plan(json_plan, timestamp)

                    chain_outputs.append({"module": "json_action_plan", "content": json_plan})

                except Exception as e:
                    print(Fore.RED + f"❌ Error generating analysis: {e}" + Style.RESET_ALL)

            # Save chained log
            save_chain_log(chain_outputs, timestamp)

            print(Fore.YELLOW + "\n" + "=" * 80 + Style.RESET_ALL)
            continue_choice = (
                input(Fore.CYAN + "Continue with another operation? (y/n): " + Style.RESET_ALL)
                .strip()
                .lower()
            )
            if continue_choice in ["n", "no", "q", "quit"]:
                print(
                    Fore.MAGENTA
                    + "\n👋 Thanks for using EQ12 God Mode Commander++!"
                    + Style.RESET_ALL
                )
                break

        # === SMART DISPATCH TEST MODE ===
        elif choice.lower() == "s":
            print(Fore.CYAN + "\n🎯 SMART DISPATCH TEST MODE" + Style.RESET_ALL)

            try:
                from executors.dispatcher import dispatcher

                print("🤖 Testing smart action classification and routing...")

                test_actions = [
                    "Check MLB betting odds for tonight's games",
                    "Analyze dropshipping trends for electronic accessories",
                    "Monitor property prices in downtown area",
                    "Scrape product data from competitor websites",
                    "Send urgent travel alert for flight delays",
                ]

                print("\n📋 Test Actions:")
                for i, action in enumerate(test_actions, 1):
                    print(f"  {i}. {action}")

                action_choice = input(
                    Fore.YELLOW
                    + f"\nSelect test action (1-{len(test_actions)}) or enter custom: "
                    + Style.RESET_ALL
                )

                if action_choice.isdigit() and 1 <= int(action_choice) <= len(test_actions):
                    test_action = test_actions[int(action_choice) - 1]
                else:
                    test_action = action_choice

                # Classify and preview dispatch
                category, confidence = dispatcher.classify_action(test_action)
                print(f"\n🎯 Classification: {category} (confidence: {confidence:.2f})")

                # Test dispatch
                priority = (
                    input(
                        Fore.YELLOW
                        + "Enter priority (urgent/short_term/long_term): "
                        + Style.RESET_ALL
                    )
                    or "urgent"
                )

                result = dispatcher.dispatch_action(test_action, priority)

                if result.get("success", False):
                    print(Fore.GREEN + "✅ Dispatch test successful!" + Style.RESET_ALL)
                else:
                    print(Fore.RED + "❌ Dispatch test failed!" + Style.RESET_ALL)

                print(f"\n📊 Result: {json.dumps(result, indent=2)}")

            except ImportError:
                print(
                    Fore.RED
                    + "❌ Smart dispatcher not available. Check executor modules."
                    + Style.RESET_ALL
                )
            except Exception as e:
                print(Fore.RED + f"❌ Test error: {e}" + Style.RESET_ALL)

        # === CONFIGURATION MODE ===
        elif choice.lower() == "c":
            print(Fore.CYAN + "\n⚙️  CONFIGURATION MODE" + Style.RESET_ALL)

            config = load_config()

            print("Current Configuration:")
            print(f"  • Auto-execute: {config.get('dispatch', {}).get('auto_execute', False)}")
            print(f"  • Telegram enabled: {config.get('telegram', {}).get('enabled', False)}")
            print(f"  • Max concurrent: {config.get('dispatch', {}).get('max_concurrent', 5)}")

            if input("\nEdit configuration? (y/n): ").lower() == "y":
                print("📝 Configuration editing not implemented in this demo.")
                print("💡 Edit config.json manually to change settings.")

        # === SCHEDULING MODE ===
        elif choice.lower() == "schedule":
            print(Fore.CYAN + "\n🗓️  TASK SCHEDULER MODE" + Style.RESET_ALL)
            print("Available modules for scheduling:")
            for k, v in MODULES.items():
                if k != "0":  # Exclude custom for scheduling
                    print(f"  [{k}] {v.replace('_', ' ').title()}")
            print("  [m] Multi-Chain Mode")

            mod_choice = input(
                Fore.YELLOW + "\nChoose module to schedule: " + Style.RESET_ALL
            ).strip()

            if mod_choice in MODULES and mod_choice != "0":
                module = MODULES[mod_choice]
                print(f"\n📋 Scheduling {module.replace('_', ' ').title()} Module")

                start_time = (
                    input(
                        Fore.YELLOW
                        + "Enter start time (HH:MM, 24h format, default 07:00): "
                        + Style.RESET_ALL
                    ).strip()
                    or "07:00"
                )
                freq = (
                    input(
                        Fore.YELLOW + "Frequency - Daily (d) or Weekly (w)? [d]: " + Style.RESET_ALL
                    )
                    .strip()
                    .lower()
                )
                daily = True if freq in ["", "d", "daily"] else False

                description = (
                    input(Fore.YELLOW + "Description (optional): " + Style.RESET_ALL).strip()
                    or f"Automated {module} execution"
                )

                if schedule_task(module, start_time, daily, description):
                    print(
                        Fore.GREEN
                        + f"\n🎉 {module.title()} scheduled successfully!"
                        + Style.RESET_ALL
                    )
                else:
                    print(Fore.RED + "\n❌ Failed to schedule task" + Style.RESET_ALL)

            elif mod_choice.lower() == "m":
                print("\n⚡ Chain Mode Scheduling")
                selection = input(
                    Fore.YELLOW
                    + "Enter module numbers (comma-separated, e.g. 1,2,4): "
                    + Style.RESET_ALL
                )
                selected_keys = [
                    x.strip()
                    for x in selection.split(",")
                    if x.strip() in MODULES and x.strip() != "0"
                ]

                if selected_keys:
                    selected_modules = [MODULES[key] for key in selected_keys]
                    chain_name = "_".join(selected_modules[:3])  # Use first 3 modules for name

                    start_time = (
                        input(Fore.YELLOW + "Enter start time (HH:MM): " + Style.RESET_ALL).strip()
                        or "08:00"
                    )
                    freq = (
                        input(
                            Fore.YELLOW
                            + "Frequency - Daily (d) or Weekly (w)? [w]: "
                            + Style.RESET_ALL
                        )
                        .strip()
                        .lower()
                    )
                    daily = True if freq in ["d", "daily"] else False

                    description = (
                        f"Chain execution: {' → '.join([m.title() for m in selected_modules])}"
                    )

                    if schedule_task(f"chain_{chain_name}", start_time, daily, description):
                        print(Fore.GREEN + "\n🎉 Chain scheduled successfully!" + Style.RESET_ALL)
                else:
                    print(Fore.RED + "❌ No valid modules selected" + Style.RESET_ALL)
            else:
                print(Fore.RED + "❌ Invalid module selection" + Style.RESET_ALL)

        # === AUTO-SETUP DEFAULT SCHEDULES ===
        elif choice.lower() == "auto":
            print(Fore.CYAN + "\n🚀 AUTO-SETUP: EQ12 AI OPS COMMANDER" + Style.RESET_ALL)
            print(
                Fore.WHITE
                + "This will create a complete autonomous AI operations schedule:"
                + Style.RESET_ALL
            )
            print("\n📅 Daily Tasks:")
            for name, config in DEFAULT_SCHEDULES["daily"].items():
                print(
                    f"   • {config['time']} - {config['module'].title()}: {config['description']}"
                )

            print("\n📊 Weekly Tasks:")
            for name, config in DEFAULT_SCHEDULES["weekly"].items():
                print(f"   • {config['time']} - {config['description']}")

            confirm = (
                input(
                    Fore.YELLOW
                    + "\n🤖 Transform your system into autonomous AI Ops Commander? (y/n): "
                    + Style.RESET_ALL
                )
                .strip()
                .lower()
            )

            if confirm in ["y", "yes", "Y"]:
                setup_default_schedules()
                print(
                    Fore.CYAN
                    + "\n🎯 Your EQ12 system is now a self-driving AI Ops Commander!"
                    + Style.RESET_ALL
                )
                print(
                    Fore.WHITE
                    + "   Check Windows Task Scheduler to monitor your automated tasks."
                    + Style.RESET_ALL
                )
            else:
                print(Fore.YELLOW + "🤚 Auto-setup cancelled" + Style.RESET_ALL)

        # === TASK MANAGEMENT ===
        elif choice.lower() == "tasks":
            print(Fore.CYAN + "\n📋 SCHEDULED TASK MANAGEMENT" + Style.RESET_ALL)

            while True:
                print("\n[1] List scheduled tasks")
                print("[2] Remove a task")
                print("[3] Remove all EQ12 tasks")
                print("[b] Back to main menu")

                task_choice = input(Fore.YELLOW + "\nSelect option: " + Style.RESET_ALL).strip()

                if task_choice == "1":
                    list_scheduled_tasks()

                elif task_choice == "2":
                    task_name = input(
                        Fore.YELLOW + "Enter task name to remove: " + Style.RESET_ALL
                    ).strip()
                    if task_name:
                        remove_scheduled_task(task_name)

                elif task_choice == "3":
                    confirm = (
                        input(
                            Fore.RED
                            + "⚠️  Remove ALL EQ12 scheduled tasks? (y/n): "
                            + Style.RESET_ALL
                        )
                        .strip()
                        .lower()
                    )
                    if confirm in ["y", "yes"]:
                        # Get all EQ12 tasks and remove them
                        try:
                            result = subprocess.run(
                                ["schtasks", "/query", "/fo", "csv", "/nh"],
                                capture_output=True,
                                text=True,
                                check=True,
                            )
                            lines = result.stdout.strip().split("\n")
                            removed_count = 0

                            for line in lines:
                                if "EQ12_" in line:
                                    parts = line.split(",")
                                    if len(parts) >= 1:
                                        task_name = parts[0].strip('"')
                                        if remove_scheduled_task(task_name):
                                            removed_count += 1

                            print(
                                Fore.GREEN
                                + f"\n✅ Removed {removed_count} EQ12 tasks"
                                + Style.RESET_ALL
                            )

                        except Exception as e:
                            print(Fore.RED + f"❌ Error removing tasks: {e}" + Style.RESET_ALL)

                elif task_choice.lower() in ["b", "back"]:
                    break
                else:
                    print(Fore.RED + "❌ Invalid option" + Style.RESET_ALL)

        # === SINGLE MODULE MODE ===
        elif choice in MODULES:
            module = MODULES[choice]

            try:
                print(
                    Fore.BLUE
                    + f"\n🔍 Loading {module.replace('_', ' ').title()} prompt..."
                    + Style.RESET_ALL
                )
                prompt = load_prompt(module)

                if module != "custom":
                    print(
                        Fore.WHITE
                        + f"\nPrompt Preview:\n{'-'*40}\n{prompt[:200]}..."
                        + Style.RESET_ALL
                    )

                output = run_prompt(prompt, module)
                logger.info(output)

                # Save the output
                save_log(module, output)

                # Ask if user wants to continue
                print(Fore.YELLOW + "\n" + "=" * 60 + Style.RESET_ALL)
                continue_choice = (
                    input(Fore.CYAN + "Continue with another module? (y/n): " + Style.RESET_ALL)
                    .strip()
                    .lower()
                )
                if continue_choice in ["n", "no", "q", "quit"]:
                    print(
                        Fore.MAGENTA
                        + "\n👋 Thanks for using EQ12 God Mode Commander++!"
                        + Style.RESET_ALL
                    )
                    break

            except Exception as e:
                print(Fore.RED + f"❌ Error: {e}" + Style.RESET_ALL)
                continue

        else:
            print(Fore.RED + "❌ Invalid choice. Try again." + Style.RESET_ALL)


if __name__ == "__main__":
    import sys

    # Handle scheduled execution via command line arguments
    if len(sys.argv) >= 3 and sys.argv[1] == "--module":
        module_name = sys.argv[2]
        is_scheduled = "--scheduled" in sys.argv

        if is_scheduled:
            print(f"🤖 [SCHEDULED] Running {module_name.title()} module...")

        try:
            if module_name in [
                "sports",
                "travel",
                "dropship",
                "housing",
                "civil_service",
                "study",
            ]:
                prompt = load_prompt(module_name)
                output = run_prompt(prompt, module_name)
                save_log(module_name, output)

                if is_scheduled:
                    print(f"✅ [SCHEDULED] {module_name.title()} completed successfully")
            else:
                print(f"❌ Unknown module: {module_name}")

        except Exception as e:
            print(f"❌ [SCHEDULED] Error in {module_name}: {e}")

    else:
        main()
