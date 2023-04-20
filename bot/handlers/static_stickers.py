import logging
import re

from telegram import Update, InputSticker
from telegram.ext import ContextTypes

from bot.converters import convert_image
from database.models import SetTypes
from bot.stickers import save_sticker
from settings import DEFAULT_NEW_STICKER_EMOJI, EMOJI_ONLY_REGEX

logger = logging.getLogger(__name__)


async def from_static_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # TODO: webp is treated as a sticker - convert
    emoji_list = update.effective_message.sticker.emoji or DEFAULT_NEW_STICKER_EMOJI
    input_sticker = InputSticker(sticker=update.effective_message.sticker.file_id, emoji_list=emoji_list)

    await save_sticker(update, context, input_sticker, SetTypes.STATIC)


async def from_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    emoji_list = tuple(re.compile(EMOJI_ONLY_REGEX).sub('', update.effective_message.caption or '')
                       or DEFAULT_NEW_STICKER_EMOJI)

    file_id = update.effective_message.photo[-1].file_id
    photo_file = await context.bot.get_file(file_id)
    photo_bytes = bytes(await photo_file.download_as_bytearray())

    input_sticker = InputSticker(sticker=convert_image(photo_bytes), emoji_list=emoji_list)
    await save_sticker(update, context, input_sticker, SetTypes.STATIC)
