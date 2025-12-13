import os
import subprocess


def test_help_runs() -> None:
    """Running --help should exit 0 and print usage."""
    python = os.environ.get("EQ12_PYTHON", "python")
    p = subprocess.run(
        [python, r"C:\EQ12\scripts\eq12_chatgpt.py", "--help"],
        capture_output=True,
        text=True,
    )
    assert p.returncode == 0
    assert "EQ12 ChatGPT wrapper" in p.stdout


def test_no_env_key_and_no_interactive(monkeypatch, tmp_path) -> None:
    """If no OPENAI_API_KEY and no interactive input, script should raise runtime error (exit != 0).
    We simulate by redirecting stdin to an empty pipe.
    """
    env = os.environ.copy()
    env.pop("OPENAI_API_KEY", None)

    python = os.environ.get("EQ12_PYTHON", "python")
    p = subprocess.run(
        [python, r"C:\EQ12\scripts\eq12_chatgpt.py", "--prompt", "hi"],
        capture_output=True,
        text=True,
        env=env,
    )
    # Should exit with non-zero because no env and non-interactive
    assert p.returncode != 0
