import random
import string

from telegram import Update, InputSticker, Sticker
from telegram.constants import StickerFormat
from telegram.ext import ContextTypes

from database.models import Set, SetTypes
from database.utils import store_user
from locales import _
from settings import DEFAULT_VIDEO_SET_NAME


async def save_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE, input_sticker: InputSticker,
                       create_new=False) -> Set:
    user = store_user(update)
    # TODO: move validation and conversion here

    new_set_title = _('sets.default_name_video', user.lang_code)

    chosen_set = None
    if not create_new:
        for user_set in Set.select().where(Set.user == user, Set.set_type == SetTypes.VIDEO):
            telegram_set = await context.bot.get_sticker_set(user_set.name)
            if len(telegram_set.stickers) < 50:
                chosen_set = user_set
                break

    if chosen_set is None:
        random_str = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
        name = DEFAULT_VIDEO_SET_NAME % (random_str, context.bot.username)

        await context.bot.create_new_sticker_set(
            user_id=user.user_id,
            name=name,
            title=new_set_title,
            sticker_format=StickerFormat.VIDEO,
            sticker_type=Sticker.REGULAR,
            stickers=[input_sticker]
        )
        chosen_set = Set.create(user=user, name=name, title=new_set_title, set_type=SetTypes.VIDEO)

    else:
        await context.bot.add_sticker_to_set(
            user_id=user.user_id,
            name=chosen_set.name,
            sticker=input_sticker
        )

    # TODO: show sticker summary

    return chosen_set
