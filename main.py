import logging

from telegram import __version__ as TG_VER

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

from telegram.ext import Application, MessageHandler, filters, CommandHandler, PicklePersistence
from handlers.static_stickers import from_static_sticker, from_photo
from handlers.commands import start_command, help_command
from handlers.errors import update_error_handler, message_error_handler
from settings import TELEGRAM_BOT_TOKEN, LOG_LEVEL, LOG_FORMAT
from database.utils import create_tables
from handlers.rename_set_conversation import rename_set_conversation

logging.basicConfig(format=LOG_FORMAT, level=LOG_LEVEL)
logger = logging.getLogger(__name__)


def main() -> None:
    create_tables()

    persistence = PicklePersistence(filepath="context_data")
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).persistence(persistence).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(rename_set_conversation)

    application.add_handler(MessageHandler(filters.Sticker.STATIC, from_static_sticker))
    application.add_handler(MessageHandler(filters.PHOTO, from_photo))

    application.add_handler(MessageHandler(filters.ALL, message_error_handler))
    application.add_error_handler(update_error_handler)

    application.run_polling()


if __name__ == '__main__':
    main()
