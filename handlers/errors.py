import html
import json
import logging
import traceback

from telegram import Update
from telegram.constants import ParseMode, MessageEntityType
from telegram.ext import ContextTypes

from database.utils import get_user
from settings import ADMIN_ID, DEBUG
from locales import _

logger = logging.getLogger(__name__)


async def update_error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    if not DEBUG:
        # traceback.format_exception returns the usual python message about an exception, but as a
        # list of strings rather than a single string, so we have to join them together.
        tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
        tb_string = "".join(tb_list)

        # Build the message with some markup and additional information about what happened.
        update_str = update.to_dict() if isinstance(update, Update) else str(update)
        message = (
            f"An exception was raised while handling an update\n"
            f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}</pre>\n\n"
            f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
            f"<pre>{html.escape(tb_string)}</pre>"
        )

        # Finally, send the message
        await context.bot.send_message(
            chat_id=ADMIN_ID, text=message[:4095], parse_mode=ParseMode.HTML
        )


async def message_error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = await get_user(update)
    message = update.effective_message

    if message.sticker and message.sticker.is_animated:
        await context.bot.send_message(user.user_id, _('errors.no_animated_stickers', user.lang_code),
                                       parse_mode=ParseMode.HTML)

    elif message.document:
        await context.bot.send_message(user.user_id, _('errors.no_documents', user.lang_code),
                                       parse_mode=ParseMode.HTML)

    elif any(entity.type == MessageEntityType.CUSTOM_EMOJI for entity in message.entities):
        await context.bot.send_message(user.user_id, _('errors.no_custom_emoji', user.lang_code),
                                       parse_mode=ParseMode.HTML)

    else:
        await context.bot.send_message(user.user_id, _('errors.default_no', user.lang_code), parse_mode=ParseMode.HTML)
