from asyncio import get_event_loop
from warnings import filterwarnings
import logging
from datetime import time
from telegram.ext import Application, MessageHandler, filters, CommandHandler, PicklePersistence, Defaults, \
    PreCheckoutQueryHandler
from telegram.constants import ParseMode

from settings import TELEGRAM_BOT_TOKEN, LOG_LEVEL, LOG_FORMAT, CONTEXT_DATA_PATH, DEBUG
from database.utils import create_tables

from bot.bot import set_bot_commands, set_bot_description, set_bot_about
from bot.handlers.commands import start_command, help_command
from bot.handlers.translate_conversation import translate_command
from bot.handlers.my_sets_conversation import my_sets_command
from bot.handlers.my_sticker_conversation import my_sticker_conversation
from bot.handlers.static_stickers import from_static_sticker, from_photo
from bot.handlers.video_stickers import from_video_sticker, from_video
from bot.handlers.animated_stickers import from_animated_sticker
from bot.handlers.documents import from_document
from bot.handlers.subscription import subscription_command, pre_checkout_query, successful_payment, \
    subscription_reminder
from bot.handlers.errors import update_error_handler, unsupported_update_error_handler, group_chat_error_handler

filterwarnings(action='ignore', category=DeprecationWarning)

logging.basicConfig(format=LOG_FORMAT, level=LOG_LEVEL)
logger = logging.getLogger(__name__)


def main() -> None:
    # Migrate the database
    create_tables()

    # Initialize the bot
    persistence = PicklePersistence(filepath=CONTEXT_DATA_PATH)
    application = Application.builder() \
        .token(TELEGRAM_BOT_TOKEN) \
        .persistence(persistence) \
        .defaults(Defaults(parse_mode=ParseMode.HTML)) \
        .build()

    # Fill out bot's profile in supported languages
    if not DEBUG:
        # TODO: test if works with parallelism
        loop = get_event_loop()
        loop.run_until_complete(set_bot_commands(application.bot))
        loop.run_until_complete(set_bot_description(application.bot))
        loop.run_until_complete(set_bot_about(application.bot))

    # Ignore all updates from non-private chats
    application.add_handler(MessageHandler(~ filters.ChatType.PRIVATE, group_chat_error_handler))

    # Add command handlers
    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(translate_command)
    application.add_handler(my_sets_command)

    # Add media handlers
    application.add_handler(my_sticker_conversation)  # Must come before the filters.Sticker.VIDEO handler
    application.add_handler(MessageHandler(filters.Sticker.STATIC, from_static_sticker))
    application.add_handler(MessageHandler(filters.Sticker.VIDEO, from_video_sticker))
    application.add_handler(MessageHandler(filters.PHOTO, from_photo))
    application.add_handler(MessageHandler(filters.VIDEO | filters.ANIMATION, from_video))
    application.add_handler(MessageHandler(filters.Document.VIDEO | filters.Document.IMAGE, from_document))
    application.add_handler(MessageHandler(filters.Sticker.ANIMATED, from_animated_sticker))

    # Payments handlers
    application.add_handler(subscription_command)
    application.add_handler(PreCheckoutQueryHandler(pre_checkout_query))
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))

    # Catch-all for the rest
    application.add_handler(MessageHandler(filters.ALL, unsupported_update_error_handler))
    application.add_error_handler(update_error_handler)

    # Schedule subscription renewal reminders
    application.job_queue.run_daily(subscription_reminder, time=time(16, 20))

    # Start receiving
    # TODO: test parallel requests with webhooks
    application.run_polling()


if __name__ == '__main__':
    # TODO: parallel requests
    #loop = get_event_loop()
    #loop.run_until_complete(main())
    #asyncio.run(main())
    main()
