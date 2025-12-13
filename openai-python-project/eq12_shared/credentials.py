import logging

# Set up logging
logger = logging.getLogger(__name__)
﻿from __future__ import annotations

import json
import os
import sys
from getpass import getpass
from pathlib import Path
from typing import Any, Callable, Dict, Optional


class CredentialError(RuntimeError):
    """Base error for EQ12 credential store issues."""


class CredentialValidationError(CredentialError):
    """Raised when a credential fails validation."""


DEFAULT_CREDENTIALS: Dict[str, Any] = {
    "openai": {
        "api_key": ""
    },
    "telegram": {
        "bot_token": "",
        "chat_id": ""
    },
    "odds_api": {
        "api_key": ""
    },
    "google": {
        "service_account": ""
    },
    "misc": {}
}


def _find_eq12_root(start: Optional[Path] = None) -> Path:
    """Locate the EQ12 root directory by walking up until keys/ exists."""
    env_root = os.getenv("EQ12_ROOT")
    if env_root:
        candidate = Path(env_root).expanduser()
        if (candidate / "keys").is_dir():
            return candidate

    current = (start or Path(__file__).resolve())
    for candidate in [current] + list(current.parents):
        if (candidate / "keys").is_dir():
            return candidate

    raise CredentialError(
        "Unable to locate EQ12 root; ensure a 'keys' directory exists or set EQ12_ROOT."
    )


class CredentialManager:
    """Simple JSON-backed credential manager with interactive prompting."""

    def __init__(
        self,
        path: Optional[Path] = None,
        interactive: Optional[bool] = None,
    ) -> None:
        self.root = _find_eq12_root(Path.cwd())
        self.path = Path(path) if path else self.root / "keys" / "credentials.json"
        self.interactive = bool(sys.stdin and sys.stdin.isatty()) if interactive is None else interactive
        self._data: Dict[str, Any] = {}
        self._load()

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------
    def get(
        self,
        key_path: str,
        prompt: Optional[str] = None,
        *,
        allow_empty: bool = False,
        validator: Optional[Callable[[str], bool]] = None,
        mask_input: bool = True,
        retry_message: Optional[str] = None,
    ) -> str:
        """Return credential value, prompting if missing/invalid."""
        message = prompt or f"Enter value for {key_path.replace('.', ' -> ')}: "
        while True:
            value = self._get_value(key_path)
            if value is None or (not value and not allow_empty):
                value = self._prompt_for_value(message, allow_empty=allow_empty, mask_input=mask_input)
                self._set_value(key_path, value)
            if validator:
                try:
                    valid = bool(validator(value))
                    last_error: Optional[Exception] = None
                except Exception as exc:  # pragma: no cover - defensive
                    valid = False
                    last_error = exc
                if not valid:
                    if last_error:
                        print(f"Credential '{key_path}' failed validation: {last_error}")
                    elif retry_message:
                        logger.info(retry_message)
                    else:
                        print(f"Credential '{key_path}' failed validation; please re-enter.")
                    value = self._prompt_for_value(message, allow_empty=allow_empty, mask_input=mask_input)
                    self._set_value(key_path, value)
                    continue
            return value

    def ensure_env(
        self,
        key_path: str,
        env_var: str,
        prompt: Optional[str] = None,
        *,
        allow_empty: bool = False,
        validator: Optional[Callable[[str], bool]] = None,
        mask_input: bool = True,
        retry_message: Optional[str] = None,
    ) -> str:
        """Fetch value and export it to the environment."""
        value = self.get(
            key_path,
            prompt,
            allow_empty=allow_empty,
            validator=validator,
            mask_input=mask_input,
            retry_message=retry_message,
        )
        os.environ[env_var] = value
        return value

    def invalidate(
        self,
        key_path: str,
        *,
        prompt: Optional[str] = None,
        allow_empty: bool = False,
        mask_input: bool = True,
    ) -> str:
        """Force re-entry of a credential."""
        message = prompt or f"Enter updated value for {key_path.replace('.', ' -> ')}: "
        value = self._prompt_for_value(message, allow_empty=allow_empty, mask_input=mask_input)
        self._set_value(key_path, value)
        return value

    def section(self, key_path: str) -> Dict[str, Any]:
        """Return a copy of a dictionary section (or empty dict)."""
        value = self._get_value(key_path)
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise CredentialError(f"Credential '{key_path}' is not a mapping; found {type(value).__name__}.")
        return json.loads(json.dumps(value))

    def as_dict(self) -> Dict[str, Any]:
        """Return a deep copy of all credentials."""
        return json.loads(json.dumps(self._data))

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _load(self) -> None:
        if self.path.exists():
            try:
                raw = self.path.read_text(encoding="utf-8")
                self._data = json.loads(raw) if raw.strip() else {}
            except json.JSONDecodeError as exc:
                raise CredentialError(f"Credentials file '{self.path}' is not valid JSON.") from exc
        else:
            self._data = json.loads(json.dumps(DEFAULT_CREDENTIALS))
            self._write()
        if self._merge_defaults(DEFAULT_CREDENTIALS, self._data):
            self._write()

    def _write(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        serialized = json.dumps(self._data, indent=2, sort_keys=True)
        tmp_path = self.path.with_suffix(".tmp")
        tmp_path.write_text(serialized, encoding="utf-8")
        tmp_path.replace(self.path)

    def _merge_defaults(self, defaults: Dict[str, Any], target: Dict[str, Any]) -> bool:
        changed = False
        for key, value in defaults.items():
            if key not in target:
                target[key] = json.loads(json.dumps(value))
                changed = True
            elif isinstance(value, dict) and isinstance(target.get(key), dict):
                if self._merge_defaults(value, target[key]):
                    changed = True
        return changed

    def _get_value(self, key_path: str) -> Optional[Any]:
        node: Any = self._data
        for part in key_path.split('.'):
            if not isinstance(node, dict) or part not in node:
                return None
            node = node[part]
        return node

    def _set_value(self, key_path: str, value: Any) -> None:
        node: Dict[str, Any] = self._data
        parts = key_path.split('.')
        for part in parts[:-1]:
            next_node = node.get(part)
            if not isinstance(next_node, dict):
                next_node = {}
                node[part] = next_node
            node = next_node
        node[parts[-1]] = value
        self._write()

    def _prompt_for_value(self, prompt: str, *, allow_empty: bool, mask_input: bool) -> str:
        if not self.interactive:
            raise CredentialError(
                f"Credential required but session is non-interactive: {prompt}"
            )
        while True:
            raw = getpass(prompt) if mask_input else input(prompt)
            value = raw.strip()
            if value or allow_empty:
                return value
            print("Value cannot be blank.")


__all__ = [
    "CredentialManager",
    "CredentialError",
    "CredentialValidationError",
    "DEFAULT_CREDENTIALS",
]