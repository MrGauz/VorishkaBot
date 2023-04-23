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

from warnings import filterwarnings
import logging
from asyncio import get_event_loop
from telegram.ext import Application, MessageHandler, filters, CommandHandler, PicklePersistence, Defaults
from telegram.constants import ParseMode

from settings import TELEGRAM_BOT_TOKEN, LOG_LEVEL, LOG_FORMAT, CONTEXT_DATA_PATH
from database.utils import create_tables

from bot.bot import set_bot_commands, set_bot_description, set_bot_about
from bot.handlers.commands import start_command, help_command
from bot.handlers.translate_conversation import translate_command
from bot.handlers.rename_set_conversation import rename_set_command
from bot.handlers.delete_set_conversation import delete_set_command
from bot.handlers.static_stickers import from_static_sticker, from_photo
from bot.handlers.video_stickers import from_video_sticker, from_video
from bot.handlers.documents import from_document
from bot.handlers.errors import update_error_handler, message_error_handler, group_chat_error_handler

filterwarnings(action="ignore", category=DeprecationWarning)

logging.basicConfig(format=LOG_FORMAT, level=LOG_LEVEL)
logger = logging.getLogger(__name__)


def main() -> None:
    # Migrate the database
    create_tables()

    # Initialize the bot
    persistence = PicklePersistence(filepath=CONTEXT_DATA_PATH)
    application = Application.builder()\
        .token(TELEGRAM_BOT_TOKEN)\
        .persistence(persistence)\
        .defaults(Defaults(parse_mode=ParseMode.HTML))\
        .build()

    # Fill out bot's profile in supported languages
    loop = get_event_loop()
    loop.run_until_complete(set_bot_commands(application.bot))
    loop.run_until_complete(set_bot_description(application.bot))
    loop.run_until_complete(set_bot_about(application.bot))

    # Ignore all updates from non-private chats
    application.add_handler(MessageHandler(~ filters.ChatType.PRIVATE, group_chat_error_handler))

    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(translate_command)
    application.add_handler(rename_set_command)
    application.add_handler(delete_set_command)

    # Add media handlers
    application.add_handler(MessageHandler(filters.Sticker.STATIC, from_static_sticker))
    application.add_handler(MessageHandler(filters.Sticker.VIDEO, from_video_sticker))
    application.add_handler(MessageHandler(filters.PHOTO, from_photo))
    application.add_handler(MessageHandler(filters.VIDEO | filters.ANIMATION, from_video))
    application.add_handler(MessageHandler(filters.Document.VIDEO | filters.Document.IMAGE, from_document))

    # Catch-all for the rest
    application.add_handler(MessageHandler(filters.ALL, message_error_handler))
    application.add_error_handler(update_error_handler)

    # Start receiving
    # TODO: test parallel requests with webhooks
    application.run_polling()


if __name__ == '__main__':
    main()
