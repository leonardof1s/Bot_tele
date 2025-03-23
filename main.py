import logging
from telegram.ext import Application
from config import TELEGRAM_BOT_TOKEN
from handlers import get_handlers


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Inicializa o bot do Telegram"""
    logger.info("Iniciando bot...")

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    handlers = get_handlers()
    for handler in handlers:
        app.add_handler(handler)

    logger.info("Bot está rodando...")
    app.run_polling()


if __name__ == "__main__":
    main()
