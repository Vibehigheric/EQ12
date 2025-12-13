import logging
import os
import subprocess
import sys
import threading
import time
from datetime import datetime, timedelta

from openai import OpenAI

# Set up logging
logger = logging.getLogger(__name__)


try:
    from openai import AuthenticationError  # type: ignore
except ImportError:  # pragma: no cover - fallback for legacy clients

    class AuthenticationError(Exception):  # type: ignore
        """Fallback when AuthenticationError is unavailable."""

        pass


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
                prompt="Enter your OpenAI API key for EQ12 God Mode Commander: ",
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


# === Modules ===
MODULES = {
    "1": "sports",
    "2": "travel",
    "3": "dropship",
    "4": "housing",
    "5": "civil_service",
    "6": "study",
}

# === Default 9-Schedule Setup ===
DEFAULT_SCHEDULES = [
    ("sports", "07:00", "Daily", "🏆 Morning sports analysis & betting optimization"),
    ("travel", "12:00", "Daily", "✈️ Travel deals & flight monitoring"),
    ("housing", "12:30", "Daily", "🏠 Real estate market tracking"),
    ("study", "18:00", "Daily", "📚 Learning & certification progress"),
    ("sports", "19:00", "Daily", "🎯 Sports results analysis & next-day prep"),
    ("sports", "08:00", "Weekly", "📊 Monday executive digest (Sports focus)"),
    ("housing", "08:15", "Weekly", "🏘️ Monday executive digest (Housing focus)"),
    (
        "civil_service",
        "08:30",
        "Weekly",
        "🏛️ Monday executive digest (Civil Service focus)",
    ),
    ("study", "20:00", "Weekly", "🎯 Sunday commander review & strategic planning"),
]

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
</Task>
"""


# === Load stored prompt ===
def load_prompt(module_name: str) -> str:
    if module_name == "custom":
        return input(Fore.YELLOW + "\nType your custom prompt:\n> " + Style.RESET_ALL)

    prompt_path = os.path.join(
        os.path.dirname(__file__),
        "eq12_godmode_runner",
        "prompts",
        f"{module_name}.txt",
    )
    if not os.path.exists(prompt_path):
        raise FileNotFoundError(f"No prompt file found for {module_name} at {prompt_path}")

    with open(prompt_path, encoding="utf-8") as f:
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
                    "content": "You are EQ12 AI OPS COMMANDER: automate, analyze, and create with maximum depth.",
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


# === Save output to logs ===
def save_log(module: str, output: str) -> bool:
    logs_dir = os.path.join(os.path.dirname(__file__), "eq12_godmode_runner", "logs")
    os.makedirs(logs_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{module}_{timestamp}.txt"

    with open(os.path.join(logs_dir, filename), "w", encoding="utf-8") as f:
        f.write("=== EQ12 AI OPS COMMANDER LOG ===\n")
        f.write(f"Module: {module.title()}\n")
        f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"{'='*50}\n\n")
        f.write(output)

    print(Fore.MAGENTA + f"📁 [Saved to logs/{filename}]" + Style.RESET_ALL)


# === Scheduling Functions ===
def get_python_executable() -> bool:
    """Get the current Python executable path"""
    return sys.executable


def schedule_task(module, start_time="07:00", frequency="Daily", description="") -> bool:
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
        days_interval = 1 if frequency == "Daily" else 7

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

        # Create task name
        task_name = f"EQ12_{module}_{frequency}_{start_time.replace(':', '')}"
        xml_filename = f"{task_name}.xml"
        xml_path = os.path.join(working_dir, xml_filename)

        # Write XML file
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
                Fore.CYAN + f"   Next run: {start_boundary} ({frequency.lower()})" + Style.RESET_ALL
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


def get_scheduled_tasks() -> bool:
    """Get list of all EQ12 scheduled tasks"""
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

        return eq12_tasks

    except subprocess.CalledProcessError:
        return []


def show_status() -> bool:
    """Show comprehensive status of all 9 default schedules"""
    print(Fore.CYAN + "\n📊 EQ12 AI OPS COMMANDER STATUS" + Style.RESET_ALL)

    existing_tasks = get_scheduled_tasks()
    existing_task_names = [task[0] for task in existing_tasks]

    print(f"\n🎯 Default Schedule Status ({len(DEFAULT_SCHEDULES)} total):")

    active_count = 0

    for i, (module, time_str, freq, description) in enumerate(DEFAULT_SCHEDULES, 1):
        # Generate expected task name pattern
        expected_pattern = f"EQ12_{module}_{freq}"

        # Check if any existing task matches this pattern
        matching_tasks = [name for name in existing_task_names if expected_pattern in name]

        if matching_tasks:
            status_icon = "✅"
            status_color = Fore.GREEN
            status_text = "ACTIVE"
            active_count += 1
        else:
            status_icon = "❌"
            status_color = Fore.RED
            status_text = "MISSING"

        print(
            f"  {i:2d}. {status_icon} {status_color}{status_text:<8}{Style.RESET_ALL} {time_str} {freq:<7} - {description}"
        )

    # Summary
    print(f"\n📈 Automation Level: {active_count}/{len(DEFAULT_SCHEDULES)} schedules active")

    if active_count == len(DEFAULT_SCHEDULES):
        print(
            Fore.GREEN
            + "🚀 FULLY AUTOMATED - Your EQ12 is a self-driving AI Ops Commander!"
            + Style.RESET_ALL
        )
    elif active_count > 0:
        print(
            Fore.YELLOW
            + f"⚡ PARTIALLY AUTOMATED - {len(DEFAULT_SCHEDULES) - active_count} schedules missing"
            + Style.RESET_ALL
        )
        print(Fore.CYAN + "💡 Use [auto] to complete full automation setup" + Style.RESET_ALL)
    else:
        print(
            Fore.RED
            + "🔴 NO AUTOMATION - Use [auto] to transform into AI Ops Commander"
            + Style.RESET_ALL
        )

    # Show all EQ12 tasks
    if existing_tasks:
        print(f"\n📋 All EQ12 Tasks ({len(existing_tasks)} total):")
        for task_name, status in existing_tasks:
            status_color = Fore.GREEN if status == "Ready" else Fore.YELLOW
            print(f"   {status_color}{task_name}{Style.RESET_ALL} - {status}")


def setup_all_defaults() -> bool:
    """Set up all 9 default schedules"""
    print(Fore.CYAN + "\n🚀 SETTING UP ALL 9 DEFAULT SCHEDULES..." + Style.RESET_ALL)
    print(
        Fore.WHITE
        + "Transforming your system into autonomous AI Ops Commander..."
        + Style.RESET_ALL
    )

    success_count = 0

    for i, (module, time_str, freq, description) in enumerate(DEFAULT_SCHEDULES, 1):
        print(
            f"\n📅 Setting up schedule {i}/{len(DEFAULT_SCHEDULES)}: {module.title()} ({time_str} {freq})"
        )

        if schedule_task(module, time_str, freq, description):
            success_count += 1

        time.sleep(0.5)  # Small delay between task creation

    print(
        Fore.GREEN
        + f"\n✅ SETUP COMPLETE! {success_count}/{len(DEFAULT_SCHEDULES)} schedules created"
        + Style.RESET_ALL
    )

    if success_count == len(DEFAULT_SCHEDULES):
        print(
            Fore.CYAN + "\n🎯 YOUR EQ12 IS NOW A SELF-DRIVING AI OPS COMMANDER!" + Style.RESET_ALL
        )
        print(
            Fore.WHITE
            + "   • Daily operations: Sports analysis, Travel monitoring, Housing tracking, Study progress"
            + Style.RESET_ALL
        )
        print(
            Fore.WHITE
            + "   • Weekly operations: Executive digests, Strategic reviews, Commander analysis"
            + Style.RESET_ALL
        )
        print(
            Fore.WHITE
            + "   • Check Windows Task Scheduler to see all automated tasks"
            + Style.RESET_ALL
        )
    else:
        print(
            Fore.YELLOW
            + "⚠️  Some tasks failed. Check Windows Task Scheduler or run as Administrator."
            + Style.RESET_ALL
        )


def list_all_tasks() -> bool:
    """List all EQ12 tasks in detail"""
    existing_tasks = get_scheduled_tasks()

    if existing_tasks:
        print(
            Fore.CYAN
            + f"\n📋 ALL EQ12 SCHEDULED TASKS ({len(existing_tasks)} found)"
            + Style.RESET_ALL
        )
        for i, (task_name, status) in enumerate(existing_tasks, 1):
            status_color = Fore.GREEN if status == "Ready" else Fore.YELLOW
            print(f"   {i:2d}. {status_color}{task_name:<40}{Style.RESET_ALL} - {status}")
    else:
        print(Fore.YELLOW + "\n📋 No EQ12 scheduled tasks found" + Style.RESET_ALL)
        print(Fore.CYAN + "💡 Use [auto] to set up autonomous AI Ops Commander" + Style.RESET_ALL)


def remove_task(task_name) -> bool:
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


def show_banner() -> bool:
    banner = """
╔═══════════════════════════════════════════════╗
║      EQ12 AI OPS COMMANDER++ 🤖🚀              ║
║   GPT-5 + Smart Dispatch + Auto-Scheduler     ║
║      Intelligence ⚡ Automation ⚡ Execution     ║
╚═══════════════════════════════════════════════╝
"""
    logger.info(Fore.CYAN + banner + Style.RESET_ALL)

    # Quick status check
    existing_tasks = get_scheduled_tasks()
    if existing_tasks:
        print(
            Fore.GREEN
            + f"📅 AI Ops Status: {len(existing_tasks)} automated tasks running"
            + Style.RESET_ALL
        )
    else:
        print(
            Fore.YELLOW
            + "📅 AI Ops Status: No scheduled automation (use [auto] to setup)"
            + Style.RESET_ALL
        )


def main() -> bool:
    show_banner()

    while True:
        print(Fore.CYAN + "\n=== EQ12 AI OPS COMMANDER MENU ===" + Style.RESET_ALL)

        # Single module options
        for k, v in MODULES.items():
            icon = "🔥"
            display_name = v.replace("_", " ").title()
            print(f"{Fore.WHITE}[{k}]{Style.RESET_ALL} {icon} {display_name}")

        # Enhanced options
        print(
            f"\n{Fore.MAGENTA}[auto]{Style.RESET_ALL} 🚀 Setup ALL 9 Default Schedules (Full AI Ops)"
        )
        print(f"{Fore.CYAN}[schedule]{Style.RESET_ALL} 📅 Schedule Single Module")
        print(f"{Fore.BLUE}[status]{Style.RESET_ALL} 📊 Show Automation Status")
        print(f"{Fore.WHITE}[tasks]{Style.RESET_ALL} 📋 List All Scheduled Tasks")
        print(f"{Fore.YELLOW}[remove]{Style.RESET_ALL} 🗑️ Remove Scheduled Task")
        print(f"{Fore.RED}[quit]{Style.RESET_ALL} 🚪 Exit")

        choice = input(Fore.YELLOW + "\nSelect option: " + Style.RESET_ALL).strip().lower()

        if choice in ["q", "quit", "exit"]:
            print(Fore.MAGENTA + "\n👋 Exiting EQ12 AI Ops Commander. Goodbye!" + Style.RESET_ALL)
            break

        # === AUTO SETUP ALL 9 DEFAULTS ===
        if choice == "auto":
            print(
                Fore.CYAN
                + "\n🚀 AUTO-SETUP: FULL AI OPS COMMANDER TRANSFORMATION"
                + Style.RESET_ALL
            )
            print(
                Fore.WHITE
                + "This will create 9 automated schedules for complete autonomous operation:"
                + Style.RESET_ALL
            )

            print("\n📅 Daily Schedules (5):")
            daily_schedules = [s for s in DEFAULT_SCHEDULES if s[2] == "Daily"]
            for module, time_str, freq, desc in daily_schedules:
                print(f"   • {time_str} - {desc}")

            print("\n📊 Weekly Schedules (4):")
            weekly_schedules = [s for s in DEFAULT_SCHEDULES if s[2] == "Weekly"]
            for module, time_str, freq, desc in weekly_schedules:
                print(f"   • {time_str} - {desc}")

            confirm = (
                input(
                    Fore.YELLOW
                    + f"\n🤖 Transform into autonomous AI Ops Commander with {len(DEFAULT_SCHEDULES)} schedules? (y/n): "
                    + Style.RESET_ALL
                )
                .strip()
                .lower()
            )

            if confirm in ["y", "yes"]:
                setup_all_defaults()
            else:
                print(Fore.YELLOW + "🤚 Auto-setup cancelled" + Style.RESET_ALL)

        # === SCHEDULE SINGLE MODULE ===
        elif choice == "schedule":
            print(Fore.CYAN + "\n📅 SCHEDULE SINGLE MODULE" + Style.RESET_ALL)
            print("Available modules:")
            for k, v in MODULES.items():
                print(f"  [{k}] {v.replace('_', ' ').title()}")

            mod_choice = input(
                Fore.YELLOW + "\nChoose module to schedule: " + Style.RESET_ALL
            ).strip()

            if mod_choice in MODULES:
                module = MODULES[mod_choice]
                print(f"\n📝 Scheduling {module.replace('_', ' ').title()} Module")

                start_time = (
                    input(
                        Fore.YELLOW + "Enter start time (HH:MM, default 07:00): " + Style.RESET_ALL
                    ).strip()
                    or "07:00"
                )
                freq_input = (
                    input(
                        Fore.YELLOW + "Frequency - Daily (d) or Weekly (w)? [d]: " + Style.RESET_ALL
                    )
                    .strip()
                    .lower()
                )
                frequency = "Daily" if freq_input in ["", "d", "daily"] else "Weekly"

                description = (
                    input(Fore.YELLOW + "Description (optional): " + Style.RESET_ALL).strip()
                    or f"Custom {module} automation"
                )

                if schedule_task(module, start_time, frequency, description):
                    print(
                        Fore.GREEN
                        + f"\n🎉 {module.title()} scheduled successfully!"
                        + Style.RESET_ALL
                    )
                else:
                    print(Fore.RED + "\n❌ Failed to schedule task" + Style.RESET_ALL)
            else:
                print(Fore.RED + "❌ Invalid module selection" + Style.RESET_ALL)

        # === SHOW STATUS ===
        elif choice == "status":
            show_status()

        # === LIST TASKS ===
        elif choice == "tasks":
            list_all_tasks()

        # === REMOVE TASK ===
        elif choice == "remove":
            existing_tasks = get_scheduled_tasks()
            if existing_tasks:
                print(Fore.CYAN + "\n🗑️ REMOVE SCHEDULED TASK" + Style.RESET_ALL)
                print("Current EQ12 tasks:")
                for i, (task_name, status) in enumerate(existing_tasks, 1):
                    print(f"  [{i}] {task_name}")
                print("  [all] Remove ALL EQ12 tasks")

                remove_choice = input(
                    Fore.YELLOW + "\nSelect task to remove (number/all): " + Style.RESET_ALL
                ).strip()

                if remove_choice.lower() == "all":
                    confirm = (
                        input(
                            Fore.RED
                            + "⚠️ Remove ALL EQ12 scheduled tasks? (y/n): "
                            + Style.RESET_ALL
                        )
                        .strip()
                        .lower()
                    )
                    if confirm in ["y", "yes"]:
                        removed_count = 0
                        for task_name, _ in existing_tasks:
                            if remove_task(task_name):
                                removed_count += 1
                        print(
                            Fore.GREEN
                            + f"\n✅ Removed {removed_count} EQ12 tasks"
                            + Style.RESET_ALL
                        )

                elif remove_choice.isdigit():
                    task_index = int(remove_choice) - 1
                    if 0 <= task_index < len(existing_tasks):
                        task_name = existing_tasks[task_index][0]
                        remove_task(task_name)
                    else:
                        print(Fore.RED + "❌ Invalid task number" + Style.RESET_ALL)
                else:
                    print(Fore.RED + "❌ Invalid selection" + Style.RESET_ALL)
            else:
                print(
                    Fore.YELLOW + "\n📋 No EQ12 scheduled tasks found to remove" + Style.RESET_ALL
                )

        # === SINGLE MODULE EXECUTION ===
        elif choice in MODULES:
            module = MODULES[choice]

            try:
                print(
                    Fore.BLUE
                    + f"\n🔍 Loading {module.replace('_', ' ').title()} prompt..."
                    + Style.RESET_ALL
                )
                prompt = load_prompt(module)

                print(
                    Fore.WHITE + f"\nPrompt Preview:\n{'-'*40}\n{prompt[:200]}..." + Style.RESET_ALL
                )

                output = run_prompt(prompt, module)
                logger.info(output)

                # Save the output
                save_log(module, output)

                # Ask if user wants to continue
                continue_choice = (
                    input(Fore.CYAN + "\nContinue with another module? (y/n): " + Style.RESET_ALL)
                    .strip()
                    .lower()
                )
                if continue_choice in ["n", "no", "q", "quit"]:
                    print(
                        Fore.MAGENTA
                        + "\n👋 Thanks for using EQ12 AI Ops Commander!"
                        + Style.RESET_ALL
                    )
                    break

            except Exception as e:
                print(Fore.RED + f"❌ Error: {e}" + Style.RESET_ALL)
                continue

        else:
            print(Fore.RED + "❌ Invalid choice. Try again." + Style.RESET_ALL)


# === Handle scheduled execution ===
def handle_scheduled_execution() -> bool:
    """Handle execution when called by Windows Task Scheduler"""
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

        return True  # Indicate scheduled execution handled

    return False  # Not a scheduled execution


if __name__ == "__main__":
    # Check if this is a scheduled execution
    if not handle_scheduled_execution():
        # Normal interactive execution
        main()
