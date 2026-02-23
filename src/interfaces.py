"""Абстракции (Protocol) для инверсии зависимостей — D в SOLID."""

from typing import Any, Protocol


class MusicPlayer(Protocol):
    """Контракт воспроизведения музыки: поиск и play. L — подстановка любой реализации."""

    def search_tracks(
        self, query: str, limit: int = 10
    ) -> list[dict[str, Any]]:
        """Поиск треков. Возвращает список с полями id, uri, name, artists, album."""
        ...

    def play_track(self, uri: str) -> str:
        """Запуск воспроизведения по URI. Возвращает сообщение об успехе или ошибке."""
        ...

    def play_track_by_query(self, query: str) -> str:
        """Поиск по запросу и воспроизведение первого результата."""
        ...


class LLMWithTools(Protocol):
    """Контракт LLM с tool calling: один вызов возвращает контент и/или tool_calls."""

    def complete(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> tuple[str | None, list[Any] | None]:
        """
        Один раунд чата. Возвращает (текст ответа или None, список tool_calls или None).
        """
        ...


class EnvValidator(Protocol):
    """Контракт проверки окружения. S — единственная ответственность."""

    def validate(self) -> None:
        """Проверяет обязательные переменные; при отсутствии — выход с сообщением."""
        ...
