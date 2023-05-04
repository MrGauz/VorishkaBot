import logging
import os
import tempfile

import emojis
from telegram import Update, InputSticker
from telegram.constants import ChatAction, StickerLimit
from telegram.ext import ContextTypes

from bot.converters import convert_video
from database.utils import store_user
from bot.stickers import save_sticker
from locales import _
from settings import DEFAULT_STICKER_EMOJI, MAX_FILE_SIZE

logger = logging.getLogger(__name__)


async def from_video_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler for converting a video sticker to a video sticker and saving it.

    :param update: Update object containing information about the incoming update.
    :param context: Callback context which contains information about the current state of the bot.
    """
    user = store_user(update)

    if not user.is_subscribed():
        await update.effective_chat.send_action(ChatAction.TYPING)
        await update.effective_message.reply_text(_('errors.not_subscribed', user.lang_code))
        return

    await update.effective_chat.send_action(ChatAction.UPLOAD_VIDEO)
    file = await update.effective_message.sticker.get_file()
    sticker_bytes = bytes(await file.download_as_bytearray())
    emoji = update.effective_message.sticker.emoji
    input_sticker = InputSticker(sticker=sticker_bytes, emoji_list=emoji)

    await update.effective_chat.send_action(ChatAction.TYPING)
    user_set = await save_sticker(update, context, input_sticker)
    if user_set:
        await update.effective_message.reply_text(_('stickers.new_saved', user.lang_code,
                                                    placeholders={'set_name': user_set.name,
                                                                  'set_title': user_set.title,
                                                                  'emoji': emoji}))


async def from_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler for converting a video to a video sticker and saving it.

    :param update: Update object containing information about the incoming update.
    :param context: Callback context which contains information about the current state of the bot.
    """
    user = store_user(update)

    if not user.is_subscribed():
        await update.effective_chat.send_action(ChatAction.TYPING)
        await update.effective_message.reply_text(_('errors.not_subscribed', user.lang_code))
        return

    mp4_filename = tempfile.mktemp(suffix='.mp4')
    emoji = tuple(emojis.get(update.effective_message.caption or ''))[
                 :StickerLimit.MAX_STICKER_EMOJI] or DEFAULT_STICKER_EMOJI

    if update.effective_message.video:
        media = update.effective_message.video
    elif update.effective_message.animation:
        media = update.effective_message.animation
    else:
        # Doesn't ever get here, it's only here to avoid warnings
        media = None

    await update.effective_chat.send_action(ChatAction.TYPING)
    if media.file_size > MAX_FILE_SIZE:
        await update.effective_message.reply_text(_('errors.file_too_big', user.lang_code))
        return

    await update.effective_message.reply_text(_('errors.takes_time_warning', user.lang_code))
    await update.effective_chat.send_action(ChatAction.UPLOAD_VIDEO)
    file = await media.get_file()
    await file.download_to_drive(mp4_filename)

    sticker_path = await convert_video(mp4_filename)

    await update.effective_chat.send_action(ChatAction.TYPING)
    if sticker_path is None:
        await update.effective_message.reply_text(_('errors.ffmpeg_failed', user.lang_code))
        return

    input_sticker = InputSticker(sticker=open(sticker_path, 'rb'), emoji_list=emoji)
    user_set = await save_sticker(update, context, input_sticker)

    if user_set:
        await update.effective_message.reply_text(_('stickers.new_saved', user.lang_code,
                                                    placeholders={'set_name': user_set.name,
                                                                  'set_title': user_set.title,
                                                                  'emoji': ''.join(emoji)}))

    os.remove(sticker_path)
