import io
import logging
import re

from PIL import Image
from telegram import Update, InputSticker
from telegram.ext import ContextTypes

from database.models import SetTypes
from bot.stickers import save_sticker
from settings import DEFAULT_NEW_STICKER_EMOJI, EMOJI_ONLY_REGEX

logger = logging.getLogger(__name__)


async def from_static_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    input_sticker = InputSticker(sticker=update.effective_message.sticker.file_id,
                                 emoji_list=update.effective_message.sticker.emoji)

    await save_sticker(update, context, input_sticker, SetTypes.STATIC)


async def from_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Get data from Telegram
    emoji_list = tuple(re.compile(EMOJI_ONLY_REGEX).sub('', update.effective_message.caption or '')
                       or DEFAULT_NEW_STICKER_EMOJI)
    file_id = update.effective_message.photo[-1].file_id
    photo_file = await context.bot.get_file(file_id)
    photo_bytes = bytes(await photo_file.download_as_bytearray())

    # Open image
    image = Image.open(io.BytesIO(photo_bytes))
    width, height = image.size

    # Quantize the image to 8 bits (256 colors)
    image = image.quantize(colors=256, method=2)

    # Resize the image by scaling
    scale = 512 / max(width, height)
    new_width = 512 if width > height else int(width * scale)
    new_height = 512 if width < height else int(height * scale)
    image = image.resize((new_width, new_height), resample=Image.LANCZOS)

    # Save image to bytes
    output_buffer = io.BytesIO()
    image.save(output_buffer, format='PNG')
    image_bytes = output_buffer.getvalue()

    # Save sticker
    input_sticker = InputSticker(sticker=image_bytes, emoji_list=emoji_list)
    await save_sticker(update, context, input_sticker, SetTypes.STATIC)
