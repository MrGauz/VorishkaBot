import logging

from telegram import __version__ as TG_VER

from database.utils import create_tables_and_seed
from handlers.commands import start

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)

if __version_info__ < (20, 0, 0, 'alpha', 1):
    raise RuntimeError(
        f'This example is not compatible with your current PTB version {TG_VER}. To view the '
        f'{TG_VER} version of this example, '
        f'visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html'
    )

from handlers.static_stickers import save_static_sticker
from settings import TELEGRAM_BOT_TOKEN, LOG_LEVEL, LOG_FORMAT
from telegram.ext import Application, MessageHandler, filters

logging.basicConfig(format=LOG_FORMAT, level=LOG_LEVEL)
logger = logging.getLogger(__name__)


def main() -> None:
    create_tables_and_seed()

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(MessageHandler(filters.COMMAND, start))
    application.add_handler(MessageHandler(filters.Sticker.STATIC, save_static_sticker))

    application.run_polling()


if __name__ == '__main__':
    main()
