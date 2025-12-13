from __future__ import annotations

"""Client wrapper for talking to the OpenAI Chat Completions API."""

import json
from collections.abc import Mapping, MutableMapping, Sequence
from typing import Any, cast

import requests

from .config import AppConfig, config

ChatMessage = Mapping[str, Any]
JsonPayload = MutableMapping[str, Any]
JsonResponse = dict[str, Any]


class ChatGPTClient:
    def __init__(
        self,
        api_key: str | None = None,
        api_url: str | None = None,
        *,
        model: str | None = None,
        timeout: int | None = None,
        session: requests.Session | None = None,
        app_config: AppConfig | None = None,
    ) -> None:
        cfg = app_config or config
        self.api_key = api_key if api_key is not None else cfg.api_key
        self.api_url = api_url if api_url is not None else cfg.api_url
        self.model = model if model is not None else cfg.model
        self.timeout = timeout if timeout is not None else cfg.timeout
        self._session = session or requests.Session()
        self._last_response_text: str = ""

    def send_message(
        self, messages: str | Sequence[ChatMessage] | Mapping[str, Any]
    ) -> str | JsonResponse:
        if isinstance(messages, str):
            text = self.get_response(messages)
            self._last_response_text = text
            return text

        payload = self._build_payload(messages)
        return self._execute_request(payload)

    def get_response(self, user_message: str) -> str:
        message: ChatMessage = {"role": "user", "content": user_message}
        result = self.send_message([message])
        if isinstance(result, dict):
            text = self._extract_text(result)
            if text is not None:
                self._last_response_text = text
                return text
            return json.dumps(result)
        self._last_response_text = result
        return result

    def receive_response(self) -> str:
        return self._last_response_text

    def _build_payload(self, messages: Sequence[ChatMessage] | Mapping[str, Any]) -> JsonPayload:
        if isinstance(messages, Sequence) and not isinstance(messages, (Mapping, str, bytes)):
            payload: JsonPayload = {"model": self.model, "messages": list(messages)}
        else:
            mapping_messages = cast(Mapping[str, Any], messages)
            payload = dict(mapping_messages)
            payload.setdefault("model", self.model)
        return payload

    def _execute_request(self, payload: JsonPayload) -> str | JsonResponse:
        if not self.api_key:
            fallback = self._offline_fallback(payload)
            self._last_response_text = fallback
            return fallback

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        try:
            response = self._session.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
            data: JsonResponse = response.json()
            cached = self._extract_text(data)
            if cached is not None:
                self._last_response_text = cached
            return data
        except requests.RequestException as exc:
            fallback = self._offline_fallback(payload, exc)
            self._last_response_text = fallback
            return fallback

    def _extract_text(self, data: Mapping[str, Any]) -> str | None:
        choices_obj = data.get("choices")
        if not isinstance(choices_obj, Sequence) or isinstance(choices_obj, (str, bytes)):
            return None
        for choice in choices_obj:
            if not isinstance(choice, Mapping):
                continue
            message_obj = choice.get("message")
            if not isinstance(message_obj, Mapping):
                continue
            content_obj = message_obj.get("content")
            if isinstance(content_obj, str):
                return content_obj
        return None

    def _offline_fallback(self, payload: Mapping[str, Any], error: Exception | None = None) -> str:
        messages_obj = payload.get("messages")
        if isinstance(messages_obj, Sequence) and not isinstance(messages_obj, (str, bytes)):
            seq = cast(Sequence[Any], messages_obj)
            if seq:
                last_obj = seq[-1]
                if isinstance(last_obj, Mapping):
                    content_obj = last_obj.get("content")
                    text = content_obj if isinstance(content_obj, str) else str(content_obj or "")
                    text = text.strip()
                    if text:
                        return text
        reason = f" ({error})" if error else ""
        return f"[no response available{reason}]"


__all__ = ["ChatGPTClient"]
