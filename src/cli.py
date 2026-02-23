import sys

import typer

from src.agent import run_agent
from src.config import check_config


app = typer.Typer(
    help="Голосовой помощник по музыке в Spotify (управление через ИИ-агента)."
)


def _run(phrase: str | None) -> None:
    check_config()

    if phrase is not None:
        phrase = phrase.strip()
    if phrase:
        reply = run_agent(phrase)
        sys.stdout.write(reply + "\n")
        return

    # Интерактивный режим
    sys.stdout.write(
        "Режим диалога. Введи фразу для агента (exit или quit — выход).\n"
    )
    while True:
        try:
            line = input("> ").strip()
        except EOFError:
            break
        if not line:
            continue
        if line.lower() in ("exit", "quit"):
            break
        reply = run_agent(line)
        sys.stdout.write(reply + "\n")


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    phrase: str | None = typer.Argument(
        None,
        help='Фраза для агента, например: "включи Bohemian Rhapsody". Без аргумента — интерактивный режим.',
    ),
) -> None:
    """Запуск агента: одна фраза или интерактивный цикл (exit/quit — выход)."""
    if ctx.invoked_subcommand is not None:
        return
    _run(phrase)


if __name__ == "__main__":
    app()
