import logging
import random
import string

from telegram import Update, Sticker, InputSticker
from telegram.constants import StickerFormat, ParseMode
from telegram.ext import ContextTypes

from database.models import Set, SetTypes
from database.utils import get_user, save_new_set
from locales import _

logger = logging.getLogger(__name__)


async def save_static_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = await get_user(update)
    sets = Set.select().where(Set.user == user, Set.set_type == SetTypes.STATIC)

    sticker_file = await update.effective_message.sticker.get_file()
    sticker_bytes = bytes(await sticker_file.download_as_bytearray())
    input_sticker = InputSticker(sticker=sticker_bytes, emoji_list=update.effective_message.sticker.emoji)

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
