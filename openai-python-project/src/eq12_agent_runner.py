from openai import OpenAI

# File: openai-python-project/src/eq12_agent_runner.py


try:
    from openai import AuthenticationError  # type: ignore
except ImportError:  # pragma: no cover - fallback for legacy clients

    class AuthenticationError(Exception):  # type: ignore
        """Fallback when AuthenticationError is unavailable."""

        pass


from eq12_shared import CredentialError, CredentialManager

credential_manager = CredentialManager()
_CLIENT: OpenAI | None = None


def get_openai_client(force_refresh: bool = False) -> OpenAI:
    """Return a cached OpenAI client backed by the shared credential store."""
    global _CLIENT
    if force_refresh or _CLIENT is None:
        api_key = credential_manager.ensure_env(
            "openai.api_key",
            "OPENAI_API_KEY",
            prompt="Enter your OpenAI API key for eq12_agent_runner: ",
        )
        _CLIENT = OpenAI(api_key=api_key)
    return _CLIENT


def run_eq12_prompt(prompt: str, *, attempt: int = 1) -> str:
    try:
        client = get_openai_client()
        response = client.chat.completions.create(
            model="gpt-5", messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except CredentialError as err:
        raise RuntimeError(f"Credential error: {err}") from err
    except Exception as exc:
        status = getattr(exc, "status_code", None)
        if (isinstance(exc, AuthenticationError) or status in {401, 403}) and attempt < 2:
            credential_manager.invalidate(
                "openai.api_key",
                prompt="OpenAI rejected the API key. Enter a new key: ",
            )
            return run_eq12_prompt(prompt, attempt=attempt + 1)
        raise


if __name__ == "__main__":
    example_prompt = "What are the benefits of using AI in healthcare?"
    try:
        result = run_eq12_prompt(example_prompt)
        print("Response from GPT-5:", result)
    except Exception as err:
        print(f"Error running prompt: {err}")
