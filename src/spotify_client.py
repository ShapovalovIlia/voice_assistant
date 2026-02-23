import logging
import os
from pathlib import Path

from spotipy import Spotify
from spotipy.cache_handler import CacheFileHandler
from spotipy.exceptions import SpotifyException
from spotipy.oauth2 import SpotifyOAuth

# Скоупы: воспроизведение и состояние плеера
SCOPE = "user-modify-playback-state user-read-playback-state"


# Путь к кэшу токенов: домашняя директория или .spotify_tokens в проекте
def _cache_path() -> Path:
    project_cache = Path.cwd() / ".spotify_tokens"
    if project_cache.parent.exists():
        return project_cache

    return Path.home() / ".voice_assistant_spotify_tokens"


def _create_spotify() -> Spotify:
    cache_path = str(_cache_path())
    cache_handler = CacheFileHandler(cache_path=cache_path)
    auth = SpotifyOAuth(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
        scope=SCOPE,
        cache_handler=cache_handler,
        open_browser=True,  # при первой авторизации открыть браузер
    )
    auth.get_access_token(as_dict=True, check_cache=True)
    return Spotify(auth_manager=auth)


def get_client() -> Spotify:
    """Возвращает авторизованный клиент Spotify (при необходимости запускает OAuth)."""
    return _create_spotify()


NO_ACTIVE_DEVICE_MSG = (
    "Нет активного устройства для воспроизведения. "
    "Включи Spotify на телефоне, в браузере или в приложении и повтори команду."
)


def search_tracks(client: Spotify, query: str, limit: int = 10) -> list[dict]:
    """
    Поиск треков по запросу.
    Возвращает список словарей с полями: id, uri, name, artists (строка), album.
    """
    result = client.search(q=query, type="track", limit=limit)
    items = result.get("tracks", {}).get("items", [])
    return [
        {
            "id": t["id"],
            "uri": t["uri"],
            "name": t["name"],
            "artists": ", ".join(a["name"] for a in t["artists"]),
            "album": t["album"]["name"],
        }
        for t in items
    ]


def play_track(client: Spotify, uri: str) -> str:
    """
    Запускает воспроизведение трека по URI.
    Возвращает сообщение об успехе или об ошибке (в т.ч. «нет активного устройства»).
    """
    spotipy_log = logging.getLogger("spotipy")
    old_level = spotipy_log.level
    spotipy_log.setLevel(logging.CRITICAL)
    try:
        client.start_playback(uris=[uri])
        return "Воспроизведение запущено."
    except SpotifyException as e:
        err = (e.msg or str(e)).upper()
        if (
            e.http_status == 404
            or "NO_ACTIVE_DEVICE" in err
            or "NO ACTIVE DEVICE" in err
        ):
            return NO_ACTIVE_DEVICE_MSG
        return f"Ошибка Spotify: {e.msg or e}"
    finally:
        spotipy_log.setLevel(old_level)


def play_track_by_query(client: Spotify, query: str) -> str:
    """Ищет трек по запросу и запускает первый результат."""
    tracks = search_tracks(client, query, limit=1)
    if not tracks:
        return f"По запросу «{query}» ничего не найдено."
    return play_track(client, tracks[0]["uri"])
