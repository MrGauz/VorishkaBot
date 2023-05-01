import logging
import os
import re
import tempfile

from telegram import Update, InputSticker
from telegram.constants import ChatAction, StickerLimit
from telegram.ext import ContextTypes

from bot.converters import convert_video
from bot.stickers import save_sticker
from database.utils import store_user
from settings import DEFAULT_STICKER_EMOJI, EMOJI_ONLY_REGEX, MAX_FILE_SIZE
from locales import _

logger = logging.getLogger(__name__)


async def from_static_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = store_user(update)
    webp_filename = tempfile.mktemp(suffix='.webp')
    emoji_list = re.compile(EMOJI_ONLY_REGEX).sub('', update.effective_message.sticker.emoji) or DEFAULT_STICKER_EMOJI

    sticker = update.effective_message.sticker
    if sticker.file_size > MAX_FILE_SIZE:
        await update.effective_chat.send_action(ChatAction.TYPING)
        await update.effective_message.reply_text(_('errors.file_too_big', user.lang_code))
        return

    await update.effective_chat.send_action(ChatAction.UPLOAD_PHOTO)
    file = await sticker.get_file()
    await file.download_to_drive(webp_filename)

    sticker_path = convert_video(webp_filename)
    await update.effective_chat.send_action(ChatAction.TYPING)
    if sticker_path is None:
        await update.effective_message.reply_text(_('errors.ffmpeg_failed', user.lang_code))
        return

    input_sticker = InputSticker(sticker=open(sticker_path, 'rb'), emoji_list=emoji_list)
    user_set = await save_sticker(update, context, input_sticker)

    if user_set:
        await update.effective_message.reply_text(_('stickers.new_saved', user.lang_code,
                                                    placeholders={'set_name': user_set.name,
                                                                  'set_title': user_set.title}))
        # TODO: display sticker summary

    os.remove(sticker_path)


async def from_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_chat.send_action(ChatAction.UPLOAD_PHOTO)
    user = store_user(update)
    png_filename = tempfile.mktemp(suffix='.png')
    emoji_list = tuple(re.compile(EMOJI_ONLY_REGEX)
                       .sub('', update.effective_message.caption or '')[:StickerLimit.MAX_STICKER_EMOJI]
                       or DEFAULT_STICKER_EMOJI)

    photo = update.effective_message.photo[-1]
    if photo.file_size > MAX_FILE_SIZE:
        await update.effective_message.reply_text(_('errors.file_too_big', user.lang_code))
        return

    file = await photo.get_file()
    await file.download_to_drive(png_filename)

    sticker_path = convert_video(png_filename)
    await update.effective_chat.send_action(ChatAction.TYPING)
    if sticker_path is None:
        await update.effective_message.reply_text(_('errors.ffmpeg_failed', user.lang_code))
        return

    input_sticker = InputSticker(sticker=open(sticker_path, 'rb'), emoji_list=emoji_list)
    user_set = await save_sticker(update, context, input_sticker)

    if user_set:
        await update.effective_message.reply_text(_('stickers.new_saved', user.lang_code,
                                                    placeholders={'set_name': user_set.name,
                                                                  'set_title': user_set.title}))
        # TODO: display sticker summary

    os.remove(sticker_path)
