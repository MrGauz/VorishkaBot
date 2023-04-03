import html
import json
import logging
import traceback

from telegram import Update
from telegram.constants import ParseMode, StickerType
from telegram.ext import ContextTypes

from settings import ADMIN_ID

logger = logging.getLogger(__name__)


async def update_error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

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
    message = update.effective_message
    if message.photo:
        # TODO: TRANSLATE
        await context.bot.send_message(update.effective_user.id, "Sorry, I can't process images yet")
    elif message.sticker.is_animated or message.sticker.is_video:
        # TODO: TRANSLATE
        await context.bot.send_message(update.effective_user.id, "Sorry, I can't process animated stickers yet")
    elif message.document:
        # TODO: TRANSLATE
        await context.bot.send_message(update.effective_user.id, "Sorry, I can't process documents yet")
    elif message.sticker and message.sticker.type == StickerType.CUSTOM_EMOJI:
        # TODO: TRANSLATE
        await context.bot.send_message(update.effective_user.id, "Sorry, I can't process custom emoji yet")
    else:
        # TODO: TRANSLATE
        await context.bot.send_message(update.effective_user.id, "Извини, брат, к такому меня жизнь не готовила")
