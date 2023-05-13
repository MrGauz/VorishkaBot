import os
import tempfile

import emojis
from telegram import Update, InputSticker
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from bot.converters import convert_tgs
from bot.stickers import save_sticker
from database.models import AnalyticsTypes
from locales import _
from database.utils import store_user, new_analytics_event
from settings import DEFAULT_STICKER_EMOJI


async def from_animated_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler for converting an animated sticker to a video sticker and saving it.

    :param update: Update object containing information about the incoming update.
    :param context: Callback context which contains information about the current state of the bot.
    """
    await update.effective_chat.send_action(ChatAction.TYPING)
    user = store_user(update)

    if not user.is_subscribed():
        await update.effective_message.reply_text(_('errors.not_subscribed', user.lang_code))
        new_analytics_event(AnalyticsTypes.NOT_SUBSCRIBED_ERROR, update, user)
        return

    await update.effective_message.reply_text(_('errors.takes_time_warning', user.lang_code))

    await update.effective_chat.send_action(ChatAction.UPLOAD_VIDEO)
    tgs_filename = tempfile.mktemp(suffix='.tgs')
    emoji = tuple(emojis.get(update.effective_message.sticker.emoji)) or DEFAULT_STICKER_EMOJI
    file = await update.message.sticker.get_file()
    await file.download_to_drive(tgs_filename)

    sticker_path = await convert_tgs(tgs_filename)

    if sticker_path is None:
        await update.effective_message.reply_text(_('errors.tgs_converter_failed', user.lang_code))
        return

    input_sticker = InputSticker(sticker=open(sticker_path, 'rb'), emoji_list=emoji)
    user_set = await save_sticker(update, context, input_sticker)

    if user_set:
        await update.effective_chat.send_action(ChatAction.TYPING)
        await update.effective_message.reply_text(_('stickers.new_saved', user.lang_code,
                                                    placeholders={'set_name': user_set.name,
                                                                  'set_title': user_set.title,
                                                                  'emoji': ''.join(emoji)}))
        new_analytics_event(AnalyticsTypes.NEW_STICKER_FROM_ANIMATED_STICKER, update, user)

    os.remove(sticker_path)
