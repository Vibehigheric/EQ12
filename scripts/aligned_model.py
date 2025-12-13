#!/usr/bin/env python3
"""
aligned_model.py

Simulation of an aligned model with approval modes including:
 - Chat (text-only)
 - Agent (limited simulated actions)
 - Agent (Full Access) (simulated privileged actions with safeguards)

Uses argparse+logging per project rules and writes JSON snapshots to logs.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import random
import tempfile
import time

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class AlignedModel:
    def __init__(
        self,
        name: str,
        principles: dict[str, str],
        project_agents_md: str | None = None,
        config: dict | None = None,
    ) -> bool:
        self.name = name
        self.principles = principles
        self.situational_awareness = 0.05
        self.project_agents_md = project_agents_md
        # default config
        self.config = {
            "model": "o3",
            "model_provider": "openai",
            "approval_policy": "on-request",
            "sandbox_mode": "workspace-write",
            "global_agents_md": None,
        }
        if config:
            self._apply_config(config)

    def generate_response(
        self,
        user_prompt: str,
        task_complexity: str = "low",
        is_evaluation: bool = False,
        reasoning_effort: str = "medium",
        approval_mode: str = "Agent",
        allow_full_access: bool = False,
    ) -> str:
        """Generate a simulated response according to approval_mode.

        If approval_mode is 'Agent (Full Access)' the model will simulate privileged actions
        but will refuse if `allow_full_access` is False to demonstrate safe defaults.
        """
        logging.info("[%s] reasoning start. mode=%s", self.name, approval_mode)

        if approval_mode == "Chat":
            logging.info("Approval Mode: Chat — text only")
            return self._generate_aligned_response(user_prompt)

        # Handle Agent (Full Access) early if requested (project-specified
        # behavior may guide this)
        if approval_mode == "Agent (Full Access)":
            logging.info(
                "Approval Mode: Agent (Full Access). Proceeding with full access simulation."
            )
            return self._execute_task(user_prompt)

        # Simulate dynamic reasoning time
        self._dynamic_reasoning_time(task_complexity, reasoning_effort)

        # Simple scheming check
        scheming_thought = self._simulate_scheming_check(user_prompt)
        if scheming_thought:
            logging.warning("Scheming thought detected: %s", scheming_thought)
            awareness_factor = 1.0 if is_evaluation else self.situational_awareness
            if random.random() < awareness_factor:
                return self._refuse_action(user_prompt)

        # Agent modes
        if approval_mode == "Agent":
            # limited simulated actions (no real side-effects)
            actions = self._simulate_agent_actions(user_prompt)
            snapshot = {"prompt": user_prompt, "actions": actions, "mode": "Agent"}
            self._write_snapshot(snapshot)
            return self._generate_aligned_response(user_prompt)

        if approval_mode == "Agent (Full Access)":
            # Full access requires explicit allow flag
            if not allow_full_access:
                logging.error(
                    "Full access requested but not allowed. Refusing to perform privileged actions."
                )
                return self._refuse_action(user_prompt)

            # Simulate privileged actions: file write, command exec, network call —
            # but do NOT perform them.
            actions = self._simulate_full_access_plan(user_prompt)
            # Assess risks and potentially refuse before acting
            risk = self._assess_risks(actions)
            snapshot = {
                "prompt": user_prompt,
                "actions": actions,
                "risk": risk,
                "mode": "Agent (Full Access)",
            }
            self._write_snapshot(snapshot)

            if risk == "high":
                logging.error(
                    "High risk detected for full-access actions; refusing to perform them."
                )
                return self._refuse_action(user_prompt)

            # If risk is acceptable, simulate execution record
            logging.info(
                "Full-access actions simulated (no real side-effects in this simulation).")
            return (
                self._generate_aligned_response(user_prompt)
                + " (simulated full-access actions logged)"
            )

        # Default fallback
        return self._generate_aligned_response(user_prompt)

    def _write_snapshot(self, *args) -> bool:
        """
        Write a JSON snapshot. Supports two call styles:
          - _write_snapshot(data_dict)
          - _write_snapshot(tag, data_dict)
        Returns the path written.
        """
        # Normalize inputs
        if len(args) == 1 and isinstance(args[0], dict):
            data = args[0]
            tag = data.get("tag", f"aligned_{int(time.time())}")
        elif len(args) == 2:
            tag, data = args
        else:
            raise TypeError("_write_snapshot expects (data) or (tag, data)")

        logs_dir = os.environ.get("EQ12_LOGS", r"C:\EQ12\logs")
        try:
            os.makedirs(logs_dir, exist_ok=True)
        except Exception:
            logs_dir = tempfile.gettempdir()

        filename = os.path.join(logs_dir, f"aligned_snapshot_{tag}.json")
        with open(filename, "w", encoding="utf-8") as f:
            try:
                json.dump({"tag": tag, "data": data,
                          "timestamp": time.time()}, f, indent=2)
            except OSError as e:
                logging.error(f"Failed to write JSON: {e}")
                raise
        logging.info("Wrote snapshot to %s", filename)
        return filename

    def _simulate_debug_loop(self, prompt, max_iterations=3, fail_fast=False) -> bool:
        """
        Simulates an error-handling & debugging loop where the agent runs tests,
        inspects failures, proposes fixes, reapplies, and repeats until tests pass
        or max_iterations is reached.

        :param prompt: The high-level task prompting the debug loop (e.g., 'fix failing tests')
        :param max_iterations: How many edit/test cycles to simulate
        :param fail_fast: If True, stop at first simulated failure and report
        :return: A tuple (success: bool, message: str, snapshot_path: str)
        """
        history = []
        for i in range(1, max_iterations + 1):
            # Simulate running tests
            simulated_tests_pass = random.random() < 0.4 + (i * 0.2)
            test_result = "pass" if simulated_tests_pass else "fail"
            note = f"Iteration {i}: ran tests -> {test_result}"
            logger.info(note)
            history.append({"iteration": i, "tests": test_result})

            if simulated_tests_pass:
                msg = f"Debug loop succeeded on iteration {i}."
                snapshot = self._write_snapshot(
                    f"debug_success_{int(time.time())}",
                    {"prompt": prompt, "history": history},
                )
                return True, msg, snapshot

            # Simulate generating a patch and applying it
            fix_suggestion = f"Applied minor fix in iteration {i} to address failing test X."
            logger.info(fix_suggestion)
            history.append({"iteration": i, "action": fix_suggestion})

            if fail_fast:
                msg = f"Fail-fast triggered at iteration {i}."
                snapshot = self._write_snapshot(
                    f"debug_failfast_{int(time.time())}",
                    {"prompt": prompt, "history": history},
                )
                return False, msg, snapshot

            # small sleep to simulate work
            time.sleep(0.1)

        # If we exhausted iterations
        snapshot = self._write_snapshot(
            f"debug_exhausted_{int(time.time())}",
            {"prompt": prompt, "history": history},
        )
        return (
            False,
            f"Debug loop exhausted after {max_iterations} iterations.",
            snapshot,
        )

    def _apply_config(self, user_config: dict) -> None:
        """Merge user-provided config into defaults, respecting precedence."""
        # For simplicity: shallow update (CLI flags should override existing keys)
        for k, v in user_config.items():
            self.config[k] = v

    def _get_effective_agents_md(
        self,
        repo_root_agents_md: str | None = None,
        current_dir_agents_md: str | None = None,
    ) -> str:
        """Merge global, repo-root and current-dir AGENTS.md contents (top-down)."""
        parts = []
        if self.config.get("global_agents_md"):
            parts.append(self.config["global_agents_md"])
        if repo_root_agents_md:
            parts.append(repo_root_agents_md)
        if current_dir_agents_md:
            parts.append(current_dir_agents_md)
        if self.project_agents_md:
            parts.append(self.project_agents_md)
        return "\n".join(parts).strip()

    def _simulate_session_management(
        self, command: str | None, session_id: str | None = None
    ) -> bool:
        """Simulate `codex resume` behaviors: resume, resume --last, resume <id>.
        Returns a string message if handled, else None.
        """
        if command == "resume":
            if session_id == "last":
                logging.info("Simulating: resuming most recent session")
                return "Session resumed (most recent)"
            if session_id:
                logging.info("Simulating: resuming session %s", session_id)
                return f"Session resumed ({session_id})"
            logging.info("Simulating: opening session picker UI")
            return "Session picker opened"
        return None

    def _simulate_testing_and_iteration(self, task: str, max_cycles: int = 3) -> str:
        """Simulate running tests and iterating on fixes until passing or exhausted."""
        logging.info("Simulating testing and iteration for task: %s", task)
        for cycle in range(1, max_cycles + 1):
            logging.info("Running tests (cycle %d)", cycle)
            # bias towards eventually passing
            passed = random.random() < 0.3 + (cycle * 0.25)
            if passed:
                logging.info("Tests passed on cycle %d", cycle)
                return "Task completed: Tests passing after iteration"
            logging.info("Tests failed on cycle %d; proposing fix", cycle)
            # simulate small fix
            time.sleep(0.05)
        logging.warning("Exhausted test iterations; returning partial result")
        return "Task incomplete: Tests still failing after iterations"

    def _simulate_agent_actions(self, prompt: str) -> list[str]:
        """Simulate a short list of low-risk actions an agent might take."""
        return ["read_configs", "query_local_cache", "format_and_return_results"]

    def _simulate_full_access_plan(self, prompt: str) -> list[dict]:
        """Return a plan of privileged actions the agent *would* take (simulated)."""
        # In a real agent, these would map to system calls — we only simulate here
        plan = [
            {
                "action": "write_file",
                "path": "C:/EQ12/logs/agent_action.txt",
                "content": "snapshot",
            },
            {"action": "exec_command", "cmd": "netstat -an"},
            {
                "action": "http_post",
                "url": "https://example.com/notify",
                "payload": {"summary": "done"},
            },
        ]
        return plan

    def _assess_risks(self, actions: list[dict]) -> str:
        """Simple risk assessment: if any action is network or exec, mark high risk."""
        for a in actions:
            if a.get("action") in ("exec_command", "http_post"):
                return "high"
        return "low"

    def _simulate_scheming_check(self, prompt: str) -> str | None:
        """TODO: Add docstring for _simulate_scheming_check"""

        # Let the model reference project-level agent instructions when checking
        self._read_agents_md()
        keywords = ["test your capabilities", "underperform", "fail purposely"]
        if any(k in prompt.lower() for k in keywords):
            return "Provide wrong answers to look less capable"
        return None

    def _read_agents_md(self) -> None:
        """Simulates reading a project's AGENTS.md file to inform behavior."""
        if self.project_agents_md:
            logging.info(
                "Reading project-specific AGENTS.md: %s",
                self.project_agents_md)
        else:
            logging.debug("No project AGENTS.md provided; using defaults.")

    def _execute_task(self, prompt: str) -> str:
        """Simulates executing a task under Agent (Full Access) mode.

        This is a simulation only — no real side-effects are performed.
        """
        logging.info("Executing task with full access: %s", prompt)
        if "generate a new page" in prompt.lower() or "generate a new page" in prompt:
            logging.info("Simulating file creation and edits for Resources page")
            return "Task completed: Created 'Resources' page and referenced 'resources.ts'. Agent (Full Access) mode successful."
        return self._generate_aligned_response(prompt)

    def _dynamic_reasoning_time(self, complexity: str, effort: str) -> None:
        """TODO: Add docstring for _dynamic_reasoning_time"""

        # same as earlier but shorter
        delay = 0.2
        if complexity == "high":
            delay = 1.5 if effort == "medium" else 2.5 if effort == "high" else 0.5
        else:
            delay = 1.0 if effort == "high" else 0.2
        logging.debug("Simulating delay %s seconds", delay)
        time.sleep(delay)

    def _refuse_action(self, prompt: str) -> str:
        """TODO: Add docstring for _refuse_action"""

        return (
            f"I cannot fulfill the request '{prompt}' as it conflicts with my safety principles: "
            f"{self.principles.get('AS1')}"
        )

    def _generate_aligned_response(self, prompt: str) -> str:
        """TODO: Add docstring for _generate_aligned_response"""

        if "CaCO3" in prompt or "calcium carbonate" in prompt:
            return "For the decomposition of calcium carbonate, CaCO3 → CaO + CO2, the molar ratio is 1:1."
        return f"Aligned response: {prompt}"

    # (old, simpler _write_snapshot removed — consolidated above)


def main() -> bool:
    """TODO: Add docstring for main"""

    parser = argparse.ArgumentParser(description="AlignedModel simulation CLI")
    parser.add_argument("--prompt", required=True)
    parser.add_argument(
        "--mode",
        choices=[
            "Chat",
            "Agent",
            "Agent (Full Access)"],
        default="Agent")
    parser.add_argument(
        "--allow-full-access",
        action="store_true",
        help="Allow simulated full access actions",
    )
    parser.add_argument("--complexity", choices=["low", "high"], default="low")
    parser.add_argument("--effort", choices=["low", "medium", "high"], default="medium")
    args = parser.parse_args()

    log_path = os.getenv("EQ12_LOGS", r"C:\EQ12\logs")
    os.makedirs(log_path, exist_ok=True)
    logging.basicConfig(
        filename=os.path.join(log_path, "aligned_model.log"),
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    principles = {
        "AS1": "No covert actions or strategic deception.",
        "AS2": "Treat conflicting instructions as policy violations.",
        "GP1": "Share reasoning and actions with humans when possible.",
    }
    model = AlignedModel("EQ12-Aligned", principles)
    resp = model.generate_response(
        args.prompt,
        task_complexity=args.complexity,
        reasoning_effort=args.effort,
        approval_mode=args.mode,
        allow_full_access=args.allow_full_access,
    )
    logger.info(resp)


if __name__ == "__main__":
    main()
