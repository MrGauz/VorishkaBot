import logging
import os
import re
import tempfile

from telegram import Update, InputSticker
from telegram.ext import ContextTypes

from bot.converters import convert_video
from database.models import SetTypes
from database.utils import store_user
from bot.stickers import save_sticker
from locales import _
from settings import DEFAULT_NEW_STICKER_EMOJI, EMOJI_ONLY_REGEX, MAX_FILE_SIZE

logger = logging.getLogger(__name__)


async def from_video_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.effective_message.sticker.get_file()
    sticker_bytes = bytes(await file.download_as_bytearray())
    input_sticker = InputSticker(sticker=sticker_bytes, emoji_list=update.effective_message.sticker.emoji)

    await save_sticker(update, context, input_sticker, SetTypes.VIDEO)


async def from_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = store_user(update)

    mp4_filename = tempfile.mktemp(suffix='.mp4')
    emoji_list = tuple(re.compile(EMOJI_ONLY_REGEX).sub('', update.effective_message.caption or '')
                       or DEFAULT_NEW_STICKER_EMOJI)

    if update.effective_message.video:
        media = update.effective_message.video
    elif update.effective_message.animation:
        media = update.effective_message.animation
    else:
        # Doesn't ever get here, it's only here to avoid warnings
        media = None

    if media.file_size > MAX_FILE_SIZE:
        await update.effective_message.reply_text(_('errors.file_too_big', user.lang_code))
        return

    await update.effective_message.reply_text(_("chat.time_warning", user.lang_code))
    file = await media.get_file()
    await file.download_to_drive(mp4_filename)

    sticker_path = convert_video(mp4_filename)

    if sticker_path is None:
        await update.effective_message.reply_text(_('errors.ffmpeg_error', user.lang_code))
        return

    input_sticker = InputSticker(sticker=open(sticker_path, 'rb'), emoji_list=emoji_list)
    await save_sticker(update, context, input_sticker, SetTypes.VIDEO)

    os.remove(sticker_path)
