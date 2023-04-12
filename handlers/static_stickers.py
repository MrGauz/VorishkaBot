import io
import logging
import random
import re
import string

from PIL import Image
from telegram import Update, Sticker, InputSticker
from telegram.constants import StickerFormat, ParseMode
from telegram.ext import ContextTypes

from database.models import Set, SetTypes
from database.utils import get_user, save_new_set
from locales import _
from settings import DEFAULT_EMOJI

logger = logging.getLogger(__name__)


async def save_static_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE, input_sticker: InputSticker) -> None:
    user = await get_user(update)
    sets = Set.select().where(Set.user == user, Set.set_type == SetTypes.STATIC)

    if sets.count() == 0:
        random_str = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
        name = "stickers_%s_by_%s" % (random_str, context.bot.username)
        title = _('sets.default_name', user.lang_code)

        await context.bot.create_new_sticker_set(
            user_id=user.user_id,
            name=name,
            title=title,
            sticker_format=StickerFormat.STATIC,
            sticker_type=Sticker.REGULAR,
            stickers=[input_sticker]
        )
        new_set = await save_new_set(user, name, title, SetTypes.STATIC)

        text = _('chat.sticker_saved_new_set', user.lang_code, {'set_name': new_set.name})
        await context.bot.send_message(chat_id=user.user_id, text=text, parse_mode=ParseMode.HTML)
    else:
        # TODO: check for available space
        chosen_set = sets.first()
        await context.bot.add_sticker_to_set(
            user_id=user.user_id,
            name=chosen_set.name,
            sticker=input_sticker
        )

        text = _('chat.sticker_saved', user.lang_code, {'set_name': chosen_set.name, 'set_title': chosen_set.title})
        await context.bot.send_message(chat_id=user.user_id, text=text, parse_mode=ParseMode.HTML)

    # TODO: show sticker summary


async def from_static_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    sticker_file = await update.effective_message.sticker.get_file()
    sticker_bytes = bytes(await sticker_file.download_as_bytearray())
    input_sticker = InputSticker(sticker=sticker_bytes, emoji_list=update.effective_message.sticker.emoji)

    await save_static_sticker(update, context, input_sticker)


async def from_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Get data from Telegram
    emoji_pattern = re.compile("[^\U0001F000-\U0001F999]+")
    emoji_list = tuple(emoji_pattern.sub('', update.effective_message.caption or '') or DEFAULT_EMOJI)

    file_id = update.effective_message.photo[-1].file_id
    photo_file = await context.bot.get_file(file_id)
    photo_bytes = bytes(await photo_file.download_as_bytearray())

    # Open image
    image = Image.open(io.BytesIO(photo_bytes))
    width, height = image.size
    max_size = 512

    # Quantize the image to 8 bits (256 colors)
    image = image.quantize(colors=256, method=2)

    # Resize the image by scaling
    scale = max_size / max(width, height)
    new_width = 512 if width > height else int(width * scale)
    new_height = 512 if width < height else int(height * scale)
    image = image.resize((new_width, new_height), resample=Image.LANCZOS)

    # Save image to bytes
    output_buffer = io.BytesIO()
    image.save(output_buffer, format='PNG')
    image_bytes = output_buffer.getvalue()

    # Save sticker
    input_sticker = InputSticker(sticker=image_bytes, emoji_list=emoji_list)
    await save_static_sticker(update, context, input_sticker)
