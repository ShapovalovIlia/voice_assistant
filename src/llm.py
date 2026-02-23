"""Реализация LLM с tool calling через OpenAI. D — зависимость от абстракции в агенте."""

from typing import Any

from openai import OpenAI


class OpenAILLM:
    """Один раунд чата с инструментами; возвращает контент и/или tool_calls."""

    def __init__(
        self, model: str = "gpt-4o-mini", client: OpenAI | None = None
    ) -> None:
        self._model = model
        self._client = client if client is not None else OpenAI()

    def complete(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> tuple[str | None, list[Any] | None]:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )
        msg = response.choices[0].message
        content = (msg.content or "").strip() or None
        tool_calls = getattr(msg, "tool_calls", None) or None
        return content, tool_calls
