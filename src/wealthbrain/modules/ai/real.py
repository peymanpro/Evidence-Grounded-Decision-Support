import httpx

from wealthbrain.modules.ai.contracts import CompletionRequest, CompletionResponse
from wealthbrain.modules.ai.provider import AIProvider, AIProviderError, AIProviderTimeoutError


class OpenAICompatibleProvider(AIProvider):
    """Minimal OpenAI-compatible chat-completions adapter.

    The adapter is intentionally small so the application depends on a stable
    provider contract instead of a vendor SDK.
    """

    def __init__(self, base_url: str, api_key: str, timeout_seconds: float = 30.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._timeout = timeout_seconds

    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        payload = {
            "model": request.model,
            "messages": [
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": request.user_prompt},
            ],
            "max_tokens": request.max_tokens,
        }
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(
                    f"{self._base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {self._api_key}"},
                    json=payload,
                )
                response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise AIProviderTimeoutError("AI provider timed out") from exc
        except httpx.HTTPError as exc:
            raise AIProviderError("AI provider request failed") from exc

        try:
            body = response.json()
            choice = body["choices"][0]["message"]["content"]
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            raise AIProviderError("AI provider returned an invalid response") from exc

        usage = body.get("usage") or {}
        return CompletionResponse(
            content=str(choice),
            provider="openai-compatible",
            model=request.model,
            input_tokens=usage.get("prompt_tokens"),
            output_tokens=usage.get("completion_tokens"),
        )
