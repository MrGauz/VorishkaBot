import logging
from asyncio import get_event_loop
from warnings import filterwarnings
from logging.config import dictConfig
from datetime import time
from telegram.ext import Application, MessageHandler, filters, CommandHandler, PicklePersistence, Defaults, \
    PreCheckoutQueryHandler
from telegram.constants import ParseMode

from bot.handlers.admin_group import add_voucher_command, list_vouchers_command, show_admin_help_message, \
    broadcast_command
from bot.handlers.vouchers import use_voucher
from bot.message_filters import voucher_message_filter, admin_group_filter
from loggers import AdminGroupHandler
from settings import TELEGRAM_BOT_TOKEN, CONTEXT_DATA_PATH, DEBUG, LOGGING_CONFIG
from database.utils import create_tables

from bot.bot import setup_bot
from bot.handlers.commands import start_command, help_command, error_command
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

dictConfig(LOGGING_CONFIG)


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

    # Log errors and higher to the admin group
    if not DEBUG:
        logger = logging.getLogger()
        handler = AdminGroupHandler(application.bot)
        handler.setLevel(logging.ERROR)
        logger.addHandler(handler)

    # Fill out bot's profile in supported languages
    if not DEBUG:
        # TODO: test if works with parallelism
        event_loop = get_event_loop()
        task = event_loop.create_task(setup_bot(application.bot))
        task.add_done_callback(lambda fut: fut.result())

    # Admin commands (only work in the ADMIN_GROUP_ID)
    application.add_handler(CommandHandler('add_voucher', add_voucher_command, filters=admin_group_filter))
    application.add_handler(CommandHandler('list_vouchers', list_vouchers_command, filters=admin_group_filter))
    application.add_handler(broadcast_command)
    application.add_handler(MessageHandler(admin_group_filter, show_admin_help_message))

    # Ignore all updates from non-private chats
    application.add_handler(MessageHandler(~filters.ChatType.PRIVATE, group_chat_error_handler))

    # Command handlers
    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('error', error_command))  # TODO: remove after tests
    application.add_handler(translate_command)
    application.add_handler(my_sets_command)

    # Media handlers
    application.add_handler(my_sticker_conversation)  # Must come before the filters.Sticker.VIDEO handler
    application.add_handler(MessageHandler(filters.Sticker.STATIC, from_static_sticker))
    application.add_handler(MessageHandler(filters.Sticker.VIDEO, from_video_sticker))
    application.add_handler(MessageHandler(filters.PHOTO, from_photo))
    application.add_handler(MessageHandler(filters.VIDEO | filters.ANIMATION, from_video))
    application.add_handler(MessageHandler(filters.Document.VIDEO | filters.Document.IMAGE, from_document))
    application.add_handler(MessageHandler(filters.Sticker.ANIMATED, from_animated_sticker))

    # Vouchers handler
    application.add_handler(MessageHandler(voucher_message_filter, use_voucher))

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
    # loop = get_event_loop()
    # loop.run_until_complete(main())
    # asyncio.run(main())
    # updater - dispatcher

    # main_loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(main_loop)
    # thread = Thread(target=main_loop.run_until_complete, args=(main(),))
    # thread.start()
    # thread.join()

    main()
