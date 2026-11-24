from .config import TOKEN
from .database import init_db
from .runtime import bot


def register_handlers():
    # Importing registers the existing decorators once, without opening a connection.
    from . import events  # noqa: F401
    from .commands import community, economy, shop, admin  # noqa: F401


def main():
    if not TOKEN:
        raise SystemExit("Configure DISCORD_TOKEN no ambiente ou no arquivo .env.")
    init_db()
    register_handlers()
    bot.run(TOKEN)


if __name__ == "__main__":
    main()
