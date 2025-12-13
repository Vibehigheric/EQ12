import argparse
import logging
import os

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

# === Credential Manager ===
credential_manager = CredentialManager()
_CLIENT: OpenAI | None = None


def get_openai_client(force_refresh: bool = False) -> OpenAI:
    """Return a cached OpenAI client backed by the shared credential store."""
    global _CLIENT
    if force_refresh or _CLIENT is None:
        api_key = credential_manager.ensure_env(
            "openai.api_key",
            "OPENAI_API_KEY",
            prompt="Enter your OpenAI API key for EQ12 Prompt Runner: ",
        )
        _CLIENT = OpenAI(api_key=api_key)
    return _CLIENT


def should_retry_openai_error(error: Exception, attempt: int) -> bool:
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


# === Load a stored prompt ===
def load_prompt(module_name: str) -> str:
    path = os.path.join(os.path.dirname(__file__), "prompts", f"{module_name}.txt")
    if not os.path.exists(path):
        raise FileNotFoundError(f"No prompt found for module: {module_name}")
    with open(path) as f:
        return f.read()


# === Run GPT-5 with pro reasoning ===
def run_prompt(prompt: str, *, attempt: int = 1) -> str:
    try:
        client = get_openai_client()
        resp = client.chat.completions.create(
            model="gpt-5",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert EQ12 + GPT-5 automation assistant.",
                },
                {"role": "user", "content": prompt},
            ],
            reasoning={"effort": "heavy"},  # Pro reasoning
            max_tokens=2500,
        )
        return resp.choices[0].message.content
    except CredentialError as err:
        print(f"Credential error: {err}")
        return f"Credential error: {err}"
    except Exception as exc:
        if should_retry_openai_error(exc, attempt):
            return run_prompt(prompt, attempt=attempt + 1)
        raise


def show_menu() -> bool:
    modules = ["sports", "travel", "dropship", "housing", "civil_service", "study"]
    print("\n=== EQ12 + GPT-5 Prompt Runner ===")
    print("Select a module to run:")
    for i, module in enumerate(modules, 1):
        print(f"{i}. {module.replace('_', ' ').title()}")
    print("0. Exit")

    while True:
        try:
            choice = input("\nEnter your choice (0-6): ").strip()
            if choice == "0":
                print("Goodbye!")
                return None

            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(modules):
                return modules[choice_idx]
            print("Invalid choice. Please enter a number between 0-6.")
        except ValueError:
            print("Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            return None


if __name__ == "__main__":
    # Check if any command line arguments are provided
    if len(os.sys.argv) > 1:
        # CLI mode
        parser = argparse.ArgumentParser(description="EQ12 + GPT-5 Prompt Runner")
        parser.add_argument(
            "module",
            choices=[
                "sports",
                "travel",
                "dropship",
                "housing",
                "civil_service",
                "study",
            ],
            help="Which module prompt to run",
        )
        args = parser.parse_args()
        selected_module = args.module
    else:
        # Menu-driven mode
        selected_module = show_menu()
        if selected_module is None:
            exit(0)

    try:
        prompt = load_prompt(selected_module)
        print(f"\n=== Running {selected_module.replace('_', ' ').title()} Module ===\n")
        output = run_prompt(prompt)

        print("\n=== GPT-5 Response ===\n")
        logger.info(output)
    except Exception as e:
        print(f"Error: {e}")
