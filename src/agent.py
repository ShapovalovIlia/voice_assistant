import json

from openai import OpenAI

from src.spotify_client import (
    get_client,
    play_track,
    play_track_by_query,
    search_tracks,
)

SYSTEM_PROMPT = """
Ты — голосовой помощник по музыке в Spotify. Пользователь может просить:
- найти треки по названию или описанию («найди Bohemian Rhapsody», «что-нибудь под бег»);
- включить трек по названию или по результату поиска («включи трек X», «включи первый из найденных»).

Используй инструменты search_tracks (поиск) и play_track (воспроизведение по URI) или play_track_by_query (поиск и воспроизведение по запросу).
Отвечай кратко и по-русски. Если произошла ошибка (например, нет активного устройства) — сообщи пользователю и подскажи, что сделать.
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_tracks",
            "description": "Поиск треков в Spotify по запросу (название, исполнитель, описание).",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Поисковый запрос",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Максимум результатов (по умолчанию 10)",
                        "default": 10,
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "play_track",
            "description": "Запустить воспроизведение трека по Spotify URI (например spotify:track:...).",
            "parameters": {
                "type": "object",
                "properties": {
                    "uri": {
                        "type": "string",
                        "description": "URI трека (spotify:track:...)",
                    },
                },
                "required": ["uri"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "play_track_by_query",
            "description": "Найти трек по запросу и сразу включить его (поиск + воспроизведение).",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Поисковый запрос (название/исполнитель)",
                    },
                },
                "required": ["query"],
            },
        },
    },
]


def _execute_tool(name: str, arguments: dict, client) -> str:
    if name == "search_tracks":
        tracks = search_tracks(
            client, arguments["query"], arguments.get("limit", 10)
        )
        if not tracks:
            return "Ничего не найдено."
        return "\n".join(
            f"{i + 1}. {t['name']} — {t['artists']} (альбом: {t['album']}) | URI: {t['uri']}"
            for i, t in enumerate(tracks)
        )
    if name == "play_track":
        return play_track(client, arguments["uri"])
    if name == "play_track_by_query":
        return play_track_by_query(client, arguments["query"])
    return f"Неизвестный инструмент: {name}"


def run_agent(user_message: str) -> str:
    """
    Обрабатывает фразу пользователя: вызывает LLM с инструментами,
    выполняет tool_calls через Spotify и возвращает финальный ответ текстом.
    """
    client_openai = OpenAI()
    client_spotify = get_client()

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    while True:
        response = client_openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )
        choice = response.choices[0]
        if not choice.message.tool_calls:
            return (choice.message.content or "").strip()

        # Добавляем ответ ассистента с tool_calls
        messages.append(choice.message)

        # Выполняем каждый вызов и добавляем результаты
        for tc in choice.message.tool_calls:
            args = (
                json.loads(tc.function.arguments)
                if isinstance(tc.function.arguments, str)
                else tc.function.arguments
            )
            result = _execute_tool(tc.function.name, args, client_spotify)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                }
            )
        # Следующая итерация: LLM получит результаты и выдаст финальный ответ или новые tool_calls
