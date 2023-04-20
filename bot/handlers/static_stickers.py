import logging
import os
import re
import tempfile

from telegram import Update, InputSticker
from telegram.ext import ContextTypes

from bot.converters import convert_video
from database.models import SetTypes
from bot.stickers import save_sticker
from database.utils import get_user
from settings import DEFAULT_NEW_STICKER_EMOJI, EMOJI_ONLY_REGEX, MAX_FILE_SIZE
from locales import _

logger = logging.getLogger(__name__)


async def from_static_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = get_user(update)
    webp_filename = tempfile.mktemp(suffix='.webp')
    emoji_list = update.effective_message.sticker.emoji or DEFAULT_NEW_STICKER_EMOJI

    sticker = update.effective_message.sticker
    if sticker.file_size > MAX_FILE_SIZE:
        await update.effective_message.reply_text(_('errors.file_too_big', user.lang_code))
        return

    file = await sticker.get_file()
    await file.download_to_drive(webp_filename)

    sticker_path = convert_video(webp_filename)
    if sticker_path is None:
        await update.effective_message.reply_text(_('errors.ffmpeg_error', user.lang_code))
        return

    input_sticker = InputSticker(sticker=open(sticker_path, 'rb'), emoji_list=emoji_list)
    await save_sticker(update, context, input_sticker, SetTypes.VIDEO)

    os.remove(sticker_path)


async def from_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = get_user(update)
    png_filename = tempfile.mktemp(suffix='.png')
    emoji_list = tuple(re.compile(EMOJI_ONLY_REGEX).sub('', update.effective_message.caption or '')
                       or DEFAULT_NEW_STICKER_EMOJI)

    photo = update.effective_message.photo[-1]
    if photo.file_size > MAX_FILE_SIZE:
        await update.effective_message.reply_text(_('errors.file_too_big', user.lang_code))
        return

    file = await photo.get_file()
    await file.download_to_drive(png_filename)

    sticker_path = convert_video(png_filename)
    if sticker_path is None:
        await update.effective_message.reply_text(_('errors.ffmpeg_error', user.lang_code))
        return

    input_sticker = InputSticker(sticker=open(sticker_path, 'rb'), emoji_list=emoji_list)
    await save_sticker(update, context, input_sticker, SetTypes.VIDEO)

    os.remove(sticker_path)
