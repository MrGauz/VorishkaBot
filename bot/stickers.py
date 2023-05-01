import json
import logging
import random
import string

from telegram import Update, InputSticker, Sticker
from telegram.constants import StickerFormat
from telegram.error import TelegramError
from telegram.ext import ContextTypes

from database.models import Set, SetTypes
from database.utils import store_user
from locales import _
from settings import DEFAULT_VIDEO_SET_NAME

logger = logging.getLogger(__name__)


async def save_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE, input_sticker: InputSticker,
                       create_new=False) -> Set | None:
    user = store_user(update)
    new_set_title = _('bot.default_video_set_name', user.lang_code)

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

        try:
            await context.bot.create_new_sticker_set(
                user_id=user.user_id,
                name=name,
                title=new_set_title,
                sticker_format=StickerFormat.VIDEO,
                sticker_type=Sticker.REGULAR,
                stickers=[input_sticker]
            )
            chosen_set = Set.create(user=user, name=name, title=new_set_title, set_type=SetTypes.VIDEO)
        except TelegramError as e:
            logger.error(f'Error creating new sticker set: {e.message}\nupdate: {json.dumps(update.to_dict())}',
                         exc_info=e)
            await update.effective_chat.send_message(_('errors.sticker_not_saved', user.lang_code))
            return None

    else:
        try:
            await context.bot.add_sticker_to_set(
                user_id=user.user_id,
                name=chosen_set.name,
                sticker=input_sticker
            )
        except TelegramError as e:
            logger.error(f'Error adding sticker to set: {e.message}\nupdate: {json.dumps(update.to_dict())}',
                         exc_info=e)
            await update.effective_chat.send_message(_('errors.sticker_not_saved', user.lang_code))
            return None

    return chosen_set
