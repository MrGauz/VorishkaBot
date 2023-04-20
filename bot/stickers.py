import random
import string

from telegram import Update, InputSticker, Sticker
from telegram.constants import ParseMode, StickerFormat
from telegram.ext import ContextTypes

from database.models import Set, SetTypes
from database.utils import get_user, save_new_set
from locales import _
from settings import DEFAULT_VIDEO_SET_NAME, DEFAULT_ANIMATED_SET_NAME, DEFAULT_EMOJI_SET_NAME


async def save_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE, input_sticker: InputSticker,
                       set_type: SetTypes) -> None:
    user = get_user(update)

    match set_type:
        case SetTypes.ANIMATED:
            sticker_format = StickerFormat.ANIMATED
            sticker_type = Sticker.REGULAR
            new_set_name = DEFAULT_ANIMATED_SET_NAME
            new_set_title = _('sets.default_name_animated', user.lang_code)
            response_message_id = 'chat.sticker_saved'
        case SetTypes.EMOJI:
            sticker_format = StickerFormat.STATIC
            sticker_type = Sticker.CUSTOM_EMOJI
            new_set_name = DEFAULT_EMOJI_SET_NAME
            new_set_title = _('sets.default_name_emoji', user.lang_code)
            response_message_id = 'chat.emoji_saved'
        case SetTypes.VIDEO | _:
            sticker_format = StickerFormat.VIDEO
            sticker_type = Sticker.REGULAR
            new_set_name = DEFAULT_VIDEO_SET_NAME
            new_set_title = _('sets.default_name_video', user.lang_code)
            response_message_id = 'chat.sticker_saved'

    chosen_set = None
    for user_set in Set.select().where(Set.user == user, Set.set_type == set_type):
        telegram_set = await context.bot.get_sticker_set(user_set.name)
        if len(telegram_set.stickers) < 50:
            chosen_set = user_set
            await context.bot.add_sticker_to_set(
                user_id=user.user_id,
                name=chosen_set.name,
                sticker=input_sticker
            )
            break

    if chosen_set is None:
        random_str = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
        name = new_set_name % (random_str, context.bot.username)

        await context.bot.create_new_sticker_set(
            user_id=user.user_id,
            name=name,
            title=new_set_title,
            sticker_format=sticker_format,
            sticker_type=sticker_type,
            stickers=[input_sticker]
        )
        chosen_set = await save_new_set(user, name, new_set_title, set_type)

    text = _(response_message_id, user.lang_code, {'set_name': chosen_set.name, 'set_title': chosen_set.title})
    await context.bot.send_message(chat_id=user.user_id, text=text, parse_mode=ParseMode.HTML)

    # TODO: show sticker summary
