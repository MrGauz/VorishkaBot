import logging
import os
import re
import tempfile

from telegram import Update, InputSticker
from telegram.constants import ChatAction, StickerLimit
from telegram.ext import ContextTypes

from bot.converters import convert_video
from database.utils import store_user
from bot.stickers import save_sticker
from locales import _
from settings import DEFAULT_STICKER_EMOJI, EMOJI_ONLY_REGEX, MAX_FILE_SIZE

logger = logging.getLogger(__name__)


async def from_video_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = store_user(update)

    if not user.is_subscribed():
        await update.effective_chat.send_action(ChatAction.TYPING)
        await update.effective_message.reply_text(_('errors.not_subscribed', user.lang_code))
        return

    await update.effective_chat.send_action(ChatAction.UPLOAD_VIDEO)
    file = await update.effective_message.sticker.get_file()
    sticker_bytes = bytes(await file.download_as_bytearray())
    emoji_list = re.compile(EMOJI_ONLY_REGEX).sub('', update.effective_message.sticker.emoji) or DEFAULT_STICKER_EMOJI
    input_sticker = InputSticker(sticker=sticker_bytes, emoji_list=emoji_list)

    await update.effective_chat.send_action(ChatAction.TYPING)
    user_set = await save_sticker(update, context, input_sticker)
    if user_set:
        await update.effective_message.reply_text(_('stickers.new_saved', user.lang_code,
                                                    placeholders={'set_name': user_set.name,
                                                                  'set_title': user_set.title}))
    # TODO: show sticker summary


async def from_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = store_user(update)

    if not user.is_subscribed():
        await update.effective_chat.send_action(ChatAction.TYPING)
        await update.effective_message.reply_text(_('errors.not_subscribed', user.lang_code))
        return

    mp4_filename = tempfile.mktemp(suffix='.mp4')
    emoji_list = tuple(re.compile(EMOJI_ONLY_REGEX)
                       .sub('', update.effective_message.caption or '')[:StickerLimit.MAX_STICKER_EMOJI]
                       or DEFAULT_STICKER_EMOJI)

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

    input_sticker = InputSticker(sticker=open(sticker_path, 'rb'), emoji_list=emoji_list)
    user_set = await save_sticker(update, context, input_sticker)

    if user_set:
        await update.effective_message.reply_text(_('stickers.new_saved', user.lang_code,
                                                    placeholders={'set_name': user_set.name,
                                                                  'set_title': user_set.title}))

    os.remove(sticker_path)
    # TODO: show sticker summary
