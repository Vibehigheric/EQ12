from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, cast


class CopilotAdapter:
    def __init__(self, client: Any):
        self.client = client

    def translate_command(self, command: str) -> dict[str, Any]:
        return {
            "model": getattr(self.client, "model", "gpt-3.5-turbo"),
            "messages": [{"role": "user", "content": command}],
        }

    def execute_command(self, command: str) -> str:
        if hasattr(self.client, "get_response"):
            response_text = self.client.get_response(command)
            return response_text if isinstance(response_text, str) else str(response_text)

        request_data = self.translate_command(command)
        response_obj = self.client.send_message(request_data)
        if isinstance(response_obj, Mapping):
            response_map = cast(Mapping[str, Any], response_obj)
            return self._extract_content(response_map)
        return str(response_obj)

    def _extract_content(self, response: Mapping[str, Any]) -> str:
        choices_obj = response.get("choices")
        if isinstance(choices_obj, Sequence) and not isinstance(choices_obj, (str, bytes)):
            choices_seq = cast(Sequence[Any], choices_obj)
            for choice_obj in choices_seq:
                if not isinstance(choice_obj, Mapping):
                    continue
                choice_map = cast(Mapping[str, Any], choice_obj)
                message_obj = choice_map.get("message")
                if not isinstance(message_obj, Mapping):
                    continue
                message_map = cast(Mapping[str, Any], message_obj)
                content_obj = message_map.get("content")
                if isinstance(content_obj, str):
                    return content_obj
        return "No response"
