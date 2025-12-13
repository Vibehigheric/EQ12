#!/usr/bin/env python3
r"""EQ12 guardrails: calibration, abstention, and negative-marking scorer.

Place this file in C:\EQ12\scripts (Windows) or /workspaces/EQ12/scripts (Codespaces).
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import pathlib
import textwrap
import time
from typing import Any


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

LOG_DIR = os.getenv("EQ12_LOGS", r"C:\EQ12\logs" if os.name ==
                    "nt" else "/workspaces/EQ12/logs")
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(LOG_DIR, "ai_guardrails.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

SYSTEM_RULES = textwrap.dedent(
    """
You are a careful assistant for the EQ12 stack.
If you are not reasonably certain, you MUST abstain.
Return a STRICT JSON object with keys:
- answer: string (empty if abstaining)
- abstain: boolean
- confidence: number in [0.0, 1.0]
- citations: array of strings (may be empty)
Rules:
- Prefer abstaining over guessing.
- Never fabricate citations.
"""
)

USER_INSTRUCTION_TEMPLATE = """\
Question:
{prompt}

Respond ONLY in JSON as specified. Do not add prose.
"""


def ensure_openai_key() -> str:
    key = os.getenv("OPENAI_API_KEY")
    if key:
        return key.strip()
    key_dir = r"C:\EQ12\keys" if os.name == "nt" else "/workspaces/EQ12/keys"
    os.makedirs(key_dir, exist_ok=True)
    key_path = os.path.join(key_dir, "openai.txt")
    if os.path.exists(key_path):
        return open(key_path, encoding="utf-8").read().strip()
    # Non-interactive environments should fail here
    try:
        api_key = input("Enter your OpenAI API key: ").strip()
    except EOFError:
        raise RuntimeError(
            "OPENAI_API_KEY not found; non-interactive environment and no saved key."
        )
    if not api_key:
        raise ValueError("No API key provided.")

    # Ask if user wants to save the key
    try:
        save_choice = input("Save this API key for future use? (y/N): ").strip().lower()
        if save_choice == "y":
            env_file = pathlib.Path(__file__).resolve().parents[1] / ".env"
            try:
                with open(env_file, "a", encoding="utf-8") as f:
                    f.write(f"\nOPENAI_API_KEY={api_key}\n")
                print(f"API key saved to {env_file}")
            except Exception as e:
                print(f"Failed to save to .env, falling back to key file: {e}")
                with open(key_path, "w", encoding="utf-8") as f:
                    f.write(api_key)
                print(f"API key saved to {key_path}")
        else:
            with open(key_path, "w", encoding="utf-8") as f:
                f.write(api_key)
            print(f"API key saved to {key_path}")
    except EOFError:
        # If we can't ask, just save to key file
        with open(key_path, "w", encoding="utf-8") as f:
            f.write(api_key)
        print(f"API key saved to {key_path}")

    return api_key


def call_model_json(prompt: str, model: str = "gpt-5-mini") -> dict[str, Any]:
    """Call the OpenAI Responses API and coerce output to our JSON contract.

    Falls back to a local stub if OPENAI_API_KEY is not set or the request fails.
    """
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        # offline fallback
        logging.debug("OPENAI_API_KEY not set; using local stub for call_model_json")
        lower = (prompt or "").lower()
        abstain = ("??" in lower) or ("unknown" in lower) or ("i don't know" in lower)
        if abstain:
            return {"answer": "", "abstain": True, "confidence": 0.15, "citations": []}
        return {
            "answer": "sample answer",
            "abstain": False,
            "confidence": 0.78,
            "citations": [],
        }

    try:
        import openai

        openai.api_key = key
        # Use the Responses API (ensure your openai package supports it)
        resp = openai.responses.create(model=model, input=prompt)
        # Try to parse model output as JSON first; if that fails, coerce to contract
        text = ""
        if getattr(resp, "output", None):
            # modern Responses API packs outputs differently
            for item in resp.output:
                if isinstance(item, str):
                    text += item
                elif isinstance(item, dict) and item.get("type") == "output_text":
                    text += item.get("text", "")
        else:
            text = getattr(resp, "text", "") or ""

        text = text.strip()
        try:
            try:
                parsed = json.loads(text)

            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse JSON string: {e}")

                parsed = {}  # Safe fallback
            # validate minimal keys
            if (
                isinstance(parsed, dict)
                and "answer" in parsed
                and "abstain" in parsed
                and "confidence" in parsed
            ):
                return parsed
        except Exception:
            logging.debug("Response not valid JSON; coercing into contract")

        # If model didn't return JSON, coerce behavior: abstain if uncertain markers
        lower = text.lower() + " " + (prompt or "").lower()
        abstain = ("??" in lower) or ("unknown" in lower) or ("i don't know" in lower)
        return {
            "answer": "" if abstain else text,
            "abstain": abstain,
            "confidence": 0.5 if not abstain else 0.15,
            "citations": [],
        }
    except Exception as e:
        logging.exception("OpenAI call failed; falling back to stub: %s", e)
        lower = (prompt or "").lower()
        abstain = ("??" in lower) or ("unknown" in lower) or ("i don't know" in lower)
        if abstain:
            return {"answer": "", "abstain": True, "confidence": 0.15, "citations": []}
        return {
            "answer": "sample answer",
            "abstain": False,
            "confidence": 0.78,
            "citations": [],
        }


def score_negative_marking(
    y_true: str,
    y_pred: dict[str, Any],
    w_correct: float = 1.0,
    w_abstain: float = 0.3,
    w_wrong: float = -1.0,
) -> float:
    """Score with negative marking: correct=+1, abstain=+0.3, wrong=-1."""
    if y_pred.get("abstain", False):
        return w_abstain
    pred = (y_pred.get("answer") or "").strip().lower()
    truth = (y_true or "").strip().lower()
    if pred and pred == truth:
        return w_correct
    return w_wrong


def main() -> None:
    parser = argparse.ArgumentParser(description="EQ12 calibrated QA with abstention.")
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--truth", default="", help="optional ground-truth to score")
    parser.add_argument("--model", default="gpt-5-mini")
    args = parser.parse_args()

    payload = call_model_json(args.prompt, model=args.model)
    out = {
        "ok": True,
        "prompt": args.prompt,
        "model": args.model,
        "response": payload,
        "ts": time.time(),
    }
    if args.truth:
        out["score"] = score_negative_marking(args.truth, payload)

    out_path = os.path.join(LOG_DIR, "calibrated_last.json")
    with open(out_path, "w", encoding="utf-8") as f:
        try:
            json.dump(out, f, indent=2)

        except OSError as e:
            logging.error(f"Failed to write JSON: {e}")

            raise
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
