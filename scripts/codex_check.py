#!/usr/bin/env python3
"""Simple Python wrapper to invoke the Codex CLI locally.
Falls back to prompting for CODEX_API_KEY if not set.
"""

import os
import pathlib
import shutil
import subprocess
import sys

# Import EQ12 standardized configuration
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))


def load_env_file():
    """Load environment variables from .env file"""
    env_file = pathlib.Path(__file__).resolve().parents[1] / ".env"
    if env_file.exists():
        try:
            with open(env_file, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip()
                        if key and value and not os.environ.get(key):
                            os.environ[key] = value
        except Exception:
            pass


# Load environment variables at startup
load_env_file()


def find_codex() -> str | None:
    codex = shutil.which("codex")
    return codex


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--cmd", "-c", default="run pytest -q")
    parser.add_argument("--install-if-missing", action="store_true")
    args = parser.parse_args()

    codex = find_codex()
    if not codex and args.install_if_missing:
        subprocess.run(["npm", "i", "-g", "@openai/codex"])
        codex = find_codex()

    if not codex:
        print("codex CLI not found. Install with: npm i -g @openai/codex", file=sys.stderr)
        return 0

    if "CODEX_API_KEY" not in os.environ:
        try:
            api_key = input(
                "Enter CODEX_API_KEY (or set CODEX_API_KEY env var): ").strip()
            if api_key:
                os.environ["CODEX_API_KEY"] = api_key
                save_choice = input(
                    "Save this API key for future use? (y/N): ").strip().lower()
                if save_choice == "y":
                    env_file = pathlib.Path(__file__).resolve().parents[1] / ".env"
                    try:
                        with open(env_file, "a", encoding="utf-8") as f:
                            f.write(f"\nCODEX_API_KEY={api_key}\n")
                        print(f"API key saved to {env_file}")
                    except Exception as e:
                        print(f"Failed to save API key: {e}", file=sys.stderr)
            else:
                print("No API key provided.", file=sys.stderr)
                return 2
        except EOFError:
            print("No CODEX_API_KEY and cannot prompt interactively.", file=sys.stderr)
            return 2

    out = subprocess.run([codex, "--dry-run", *args.cmd.split()],
                         capture_output=True, text=True)
    with open("codex-output.txt", "w", encoding="utf-8") as f:
        f.write(out.stdout)
        f.write("\n\nSTDERR:\n")
        f.write(out.stderr)

    print("Codex output saved to codex-output.txt")
    return out.returncode


if __name__ == "__main__":
    raise SystemExit(main())
