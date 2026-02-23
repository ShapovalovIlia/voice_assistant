import os
import sys

from dotenv import load_dotenv


load_dotenv()


REQUIRED = [
    "SPOTIFY_CLIENT_ID",
    "SPOTIFY_CLIENT_SECRET",
    "SPOTIFY_REDIRECT_URI",
    "OPENAI_API_KEY",
]


def check_config() -> None:
    """Проверяет наличие обязательных переменных. При отсутствии — выводит ошибку и выходит."""
    missing = [k for k in REQUIRED if not os.getenv(k)]
    if missing:
        msg = (
            f"Не заданы переменные окружения: {', '.join(missing)}. "
            "Создайте приложение в Spotify Dashboard и задайте SPOTIFY_* и OPENAI_API_KEY в .env или .envrc."
        )
        sys.stderr.write(msg + "\n")
        sys.exit(1)
