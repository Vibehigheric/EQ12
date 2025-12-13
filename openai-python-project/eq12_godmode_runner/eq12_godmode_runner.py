import json
import logging
import os
import subprocess
import threading
import time
from datetime import datetime

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
                prompt="Enter your OpenAI API key for EQ12 God Mode: ",
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
                    "content": "You are EQ12 GOD MODE: automate, analyze, and create with maximum depth.",
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
You are the EQ12 GOD MODE COMMANDER. Analyze these multiple automation outputs and create:

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
You are EQ12 GOD MODE COMMANDER creating a structured action plan for automation systems.

TASK: Analyze the module outputs and create a JSON action plan with this EXACT structure:

{{
  "urgent": [
    {{"task": "description", "module": "source_module", "priority": "high", "deadline": "timeframe"}},
    {{"task": "description", "module": "source_module", "priority": "critical", "deadline": "timeframe"}}
  ],
  "short_term": [
    {{"task": "description", "module": "source_module", "timeline": "1-4 weeks", "dependencies": []}},
    {{"task": "description", "module": "source_module", "timeline": "2-3 weeks", "dependencies": ["task1"]}}
  ],
  "long_term": [
    {{"task": "description", "module": "source_module", "timeline": "1-6 months", "impact": "expected_outcome"}},
    {{"task": "description", "module": "source_module", "timeline": "3-6 months", "impact": "expected_outcome"}}
  ],
  "automation_opportunities": [
    {{"process": "what_to_automate", "modules": ["module1", "module2"], "complexity": "low|medium|high"}},
    {{"process": "what_to_automate", "modules": ["module1"], "complexity": "low|medium|high"}}
  ],
  "success_metrics": [
    {{"metric": "measurement_name", "target": "goal_value", "tracking": "how_to_measure"}},
    {{"metric": "measurement_name", "target": "goal_value", "tracking": "how_to_measure"}}
  ],
  "cross_module_synergies": [
    {{"modules": ["module1", "module2"], "synergy": "how_they_work_together", "benefit": "expected_outcome"}}
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
"""
    return run_prompt(json_prompt, "JSON Action Plan")


# === Validate and save JSON ===
def save_json_action_plan(json_content: str, timestamp: str) -> bool:
    try:
        import re

        # Extract JSON from response if it contains extra text
        json_match = re.search(r"\{.*\}", json_content, re.DOTALL)
        if json_match:
            clean_json = json_match.group()
            parsed = json.loads(clean_json)

            # Save the JSON file
            logs_dir = os.path.join(os.path.dirname(__file__), "logs")
            json_path = os.path.join(logs_dir, f"action_plan_{timestamp}.json")

            with open(json_path, "w", encoding="utf-8") as f:
                try:

                    json.dump(parsed, f, indent=2, ensure_ascii=False)

                except OSError as e:

                    logging.error(f"Failed to write JSON: {e}")

                    raise

            print(
                Fore.CYAN
                + f"📋 [JSON Action Plan saved to logs/action_plan_{timestamp}.json]"
                + Style.RESET_ALL
            )
            return True
        print(Fore.RED + "❌ Could not extract valid JSON from response" + Style.RESET_ALL)
        # Save raw content for debugging
        logs_dir = os.path.join(os.path.dirname(__file__), "logs")
        debug_path = os.path.join(logs_dir, f"action_plan_debug_{timestamp}.txt")
        with open(debug_path, "w", encoding="utf-8") as f:
            f.write(json_content)
        print(
            Fore.YELLOW
            + f"💾 [Raw JSON response saved for debugging: logs/action_plan_debug_{timestamp}.txt]"
            + Style.RESET_ALL
        )
        return False

    except json.JSONDecodeError as e:
        print(Fore.RED + f"❌ JSON validation failed: {e}" + Style.RESET_ALL)
        return False
    except Exception as e:
        print(Fore.RED + f"❌ Error saving JSON: {e}" + Style.RESET_ALL)
        return False


# === Save output to logs ===
def save_log(module: str, output: str) -> bool:
    logs_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(logs_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{module}_{timestamp}.txt" if module != "custom" else f"custom_{timestamp}.txt"

    with open(os.path.join(logs_dir, filename), "w", encoding="utf-8") as f:
        f.write("=== EQ12 GOD MODE LOG ===\n")
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
        f.write("=== EQ12 GOD MODE COMMANDER - CHAIN EXECUTION LOG ===\n")
        f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(
            f"Modules Executed: {len([o for o in chain_outputs if o['module'] != 'executive_summary'])}\n"
        )
        f.write("=" * 80 + "\n\n")

        for output in chain_outputs:
            module_name = output["module"].replace("_", " ").title()
            f.write(f"\n{'='*20} {module_name.upper()} {'='*20}\n")
            f.write(output["content"])
            f.write(f"\n{'='*60}\n")

    print(Fore.CYAN + f"📊 [Chain log saved to logs/{chain_filename}]" + Style.RESET_ALL)


# === Load dispatcher configuration ===
def load_dispatcher_config() -> bool:
    """Load dispatcher configuration for auto-execution"""
    config_path = os.path.join(os.path.dirname(__file__), "dispatcher_config.json")
    if not os.path.exists(config_path):
        return {"execution": {"auto_execute": False}, "dispatchers": {}}

    with open(config_path) as f:
        return json.load(f)


# === Execute action via dispatcher ===
def execute_action(action_text: str, action_type: str, config: dict) -> bool:
    """Execute an action using appropriate dispatcher"""

    dispatchers = config.get("dispatchers", {})
    telegram_config = config.get("telegram", {})

    # Find matching dispatcher
    matched_dispatcher = None
    for name, dispatcher in dispatchers.items():
        keywords = dispatcher.get("keywords", [])
        if any(keyword.lower() in action_text.lower() for keyword in keywords):
            matched_dispatcher = dispatcher
            matched_name = name
            break

    if not matched_dispatcher:
        print(Fore.YELLOW + f"⚠️  No dispatcher found for: {action_text[:50]}..." + Style.RESET_ALL)
        return False

    print(Fore.BLUE + f"🚀 Executing via {matched_name} dispatcher..." + Style.RESET_ALL)

    try:
        dispatcher_type = matched_dispatcher.get("type", "script")
        script_path = matched_dispatcher.get("script", "")

        if dispatcher_type == "telegram":
            # Telegram execution
            if not telegram_config.get("enabled", False):
                print(Fore.RED + "Telegram dispatch is disabled" + Style.RESET_ALL)
                return False

            try:
                bot_token = credential_manager.ensure_env(
                    "telegram.bot_token",
                    "TELEGRAM_BOT_TOKEN",
                    prompt="Enter Telegram bot token: ",
                    mask_input=False,
                )
                chat_id = credential_manager.ensure_env(
                    "telegram.chat_id",
                    "TELEGRAM_CHAT_ID",
                    prompt="Enter Telegram chat id: ",
                    mask_input=False,
                )
            except CredentialError as err:
                print(Fore.RED + f"Telegram credential error: {err}" + Style.RESET_ALL)
                return False

            cmd = ["python", script_path, action_text, bot_token, chat_id]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        elif dispatcher_type == "notebook":
            # Jupyter notebook execution
            cmd = [
                "jupyter",
                "nbconvert",
                "--execute",
                "--to",
                "html",
                script_path,
                "--ExecutePreprocessor.kernel_name=python3",
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        else:
            # Regular script execution
            cmd = ["python", script_path, action_text]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        if result.returncode == 0:
            print(Fore.GREEN + f"✅ {matched_name} executed successfully" + Style.RESET_ALL)
            if result.stdout:
                print(Fore.WHITE + f"Output: {result.stdout.strip()}" + Style.RESET_ALL)
            return True
        print(Fore.RED + f"❌ {matched_name} execution failed" + Style.RESET_ALL)
        if result.stderr:
            print(Fore.RED + f"Error: {result.stderr.strip()}" + Style.RESET_ALL)
        return False

    except subprocess.TimeoutExpired:
        print(Fore.RED + f"⏰ {matched_name} execution timed out" + Style.RESET_ALL)
        return False
    except Exception as e:
        print(Fore.RED + f"❌ Error executing {matched_name}: {e}" + Style.RESET_ALL)
        return False


# === Auto-dispatch JSON actions ===
def auto_dispatch_actions(json_plan: dict, config: dict) -> bool:
    """Auto-dispatch actions from JSON plan"""

    if not config.get("execution", {}).get("auto_execute", False):
        return

    print(Fore.CYAN + "\n⚡ AUTO-DISPATCH MODE ACTIVATED ⚡" + Style.RESET_ALL)

    total_actions = 0
    successful_executions = 0

    # Process urgent actions first
    for action in json_plan.get("urgent", []):
        if config.get("execution", {}).get("confirm_before_run", True):
            confirm = input(
                Fore.YELLOW + f"Execute URGENT: '{action[:60]}...'? (y/n): " + Style.RESET_ALL
            )
            if confirm.lower() != "y":
                continue

        total_actions += 1
        if execute_action(action, "urgent", config):
            successful_executions += 1
        time.sleep(1)  # Brief pause between executions

    # Process short-term actions
    for action in json_plan.get("short_term", []):
        if config.get("execution", {}).get("confirm_before_run", True):
            confirm = input(
                Fore.YELLOW + f"Execute SHORT-TERM: '{action[:60]}...'? (y/n): " + Style.RESET_ALL
            )
            if confirm.lower() != "y":
                continue

        total_actions += 1
        if execute_action(action, "short_term", config):
            successful_executions += 1
        time.sleep(1)

    # Summary
    print(Fore.MAGENTA + "\n📊 AUTO-DISPATCH SUMMARY:" + Style.RESET_ALL)
    print(Fore.WHITE + f"   Total Actions: {total_actions}" + Style.RESET_ALL)
    print(Fore.GREEN + f"   Successful: {successful_executions}" + Style.RESET_ALL)
    print(Fore.RED + f"   Failed: {total_actions - successful_executions}" + Style.RESET_ALL)


# === Show colorful banner ===
def show_banner() -> bool:
    banner = """
╔═══════════════════════════════════════╗
║           EQ12 GOD MODE 🚀            ║
║     GPT-5 Pro Reasoning Runner        ║
╚═══════════════════════════════════════╝
"""
    logger.info(Fore.CYAN + banner + Style.RESET_ALL)
    if not COLORS_AVAILABLE:
        print(
            Fore.YELLOW
            + "💡 Tip: Install colorama for enhanced colors: pip install colorama"
            + Style.RESET_ALL
        )


def main() -> bool:
    show_banner()

    while True:
        print(Fore.CYAN + "\n=== EQ12 GOD MODE COMMANDER ===" + Style.RESET_ALL)

        # Single module options
        for k, v in MODULES.items():
            icon = "✨" if k == "0" else "🔥"
            display_name = "Custom Prompt" if v == "custom" else v.replace("_", " ").title()
            print(f"{Fore.WHITE}[{k}]{Style.RESET_ALL} {icon} {display_name}")

        # Chain mode options
        print(f"{Fore.YELLOW}[m]{Style.RESET_ALL} ⚡ Multi-Chain Mode (run multiple modules)")
        print(f"{Fore.CYAN}[d]{Style.RESET_ALL} 🤖 Dispatch Mode (test action execution)")
        print(f"{Fore.RED}[q]{Style.RESET_ALL} 🚪 Quit")

        choice = input(Fore.YELLOW + "\nSelect option: " + Style.RESET_ALL).strip()

        if choice.lower() in ["q", "quit", "exit"]:
            print(Fore.MAGENTA + "\n👋 Exiting EQ12 God Mode Commander. Goodbye!" + Style.RESET_ALL)
            break

        # === CHAIN MODE ===
        if choice.lower() == "m":
            print(Fore.CYAN + "\n⚡ CHAIN MODE ACTIVATED ⚡" + Style.RESET_ALL)
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
                    + f"\n� Step {i}/{len(selected_modules)}: {module.title()}"
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
                    except:
                        print(Fore.WHITE + json_plan[:300] + "..." + Style.RESET_ALL)

                    # Save JSON action plan
                    save_json_action_plan(json_plan, timestamp)

                    chain_outputs.append({"module": "json_action_plan", "content": json_plan})

                    # Auto-dispatch actions if enabled
                    dispatcher_config = load_dispatcher_config()
                    if dispatcher_config.get("execution", {}).get("auto_execute", False):
                        try:
                            import re

                            json_match = re.search(r"\{.*\}", json_plan, re.DOTALL)
                            if json_match:
                                parsed_json = json.loads(json_match.group())
                                auto_dispatch_actions(parsed_json, dispatcher_config)
                        except Exception as e:
                            print(Fore.RED + f"❌ Auto-dispatch error: {e}" + Style.RESET_ALL)
                    else:
                        print(
                            Fore.YELLOW
                            + "\n💡 Tip: Enable auto_execute in dispatcher_config.json for automatic action execution"
                            + Style.RESET_ALL
                        )

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
                    + "\n👋 Thanks for using EQ12 God Mode Commander!"
                    + Style.RESET_ALL
                )
                break

        # === DISPATCH TEST MODE ===
        elif choice.lower() == "d":
            print(Fore.CYAN + "\n🤖 DISPATCH TEST MODE" + Style.RESET_ALL)

            dispatcher_config = load_dispatcher_config()
            dispatchers = dispatcher_config.get("dispatchers", {})

            print("Available dispatchers:")
            for name, dispatcher in dispatchers.items():
                print(
                    f"  • {name}: {dispatcher.get('type', 'script')} ({', '.join(dispatcher.get('keywords', [])[:3])})"
                )

            test_action = input(Fore.YELLOW + "\nEnter test action text: " + Style.RESET_ALL)
            if test_action.strip():
                print(Fore.BLUE + f"\n🚀 Testing dispatch for: '{test_action}'" + Style.RESET_ALL)
                success = execute_action(test_action, "test", dispatcher_config)
                if success:
                    print(Fore.GREEN + "✅ Dispatch test successful!" + Style.RESET_ALL)
                else:
                    print(Fore.RED + "❌ Dispatch test failed!" + Style.RESET_ALL)

            continue

        # === SINGLE MODULE MODE ===
        elif choice in MODULES:
            module = MODULES[choice]

            try:
                print(
                    Fore.BLUE
                    + f"\n� Loading {module.replace('_', ' ').title()} prompt..."
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
                    print(Fore.MAGENTA + "\n👋 Thanks for using EQ12 God Mode!" + Style.RESET_ALL)
                    break

            except Exception as e:
                print(Fore.RED + f"❌ Error: {e}" + Style.RESET_ALL)
                continue

        else:
            print(Fore.RED + "❌ Invalid choice. Try again." + Style.RESET_ALL)


if __name__ == "__main__":
    main()
