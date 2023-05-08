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


async def save_sticker_to_set(update: Update, context: ContextTypes.DEFAULT_TYPE, input_sticker: InputSticker,
                              set_name: str) -> Set | None:
    """
    Save a sticker to the specified set.

    :param update: Telegram Update object.
    :param context: Telegram bot context.
    :param input_sticker: The sticker to be saved.
    :param set_name: The name of the set to which the sticker should be saved.
    :return: The Set object for the set to which the sticker was saved, or None if the save failed.
    """
    user = store_user(update)

    found_set = None
    for user_set in Set.select().where(Set.user == user, Set.set_type == SetTypes.VIDEO, Set.name == set_name):
        telegram_set = await context.bot.get_sticker_set(user_set.name)
        if len(telegram_set.stickers) < 50:
            found_set = user_set
            break
        else:
            await update.effective_message.reply_text(_('error.move_set_full', user.lang_code))

    if found_set is None:
        return None

    result = await context.bot.add_sticker_to_set(
        user_id=user.user_id,
        name=found_set.name,
        sticker=input_sticker
    )

    if not result:
        return None

    return found_set


async def save_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE, input_sticker: InputSticker,
                       create_new=False) -> Set | None:
    """
    Save a sticker to the user's sticker set. If there is no space in the user's existing sets or
    if create_new is True, it creates a new set.

    :param update: Telegram Update object.
    :param context: Telegram bot context.
    :param input_sticker: The sticker to be saved.
    :param create_new: (optional) If True, always create a new sticker set.
    :return: The Set object for the set to which the sticker was saved, or None if the save failed.
    """
    user = store_user(update)

    chosen_set = None
    if not create_new:
        for user_set in Set.select().where(Set.user == user, Set.set_type == SetTypes.VIDEO):
            telegram_set = await context.bot.get_sticker_set(user_set.name)
            if len(telegram_set.stickers) < 50:
                # Warn if the set will be full after adding the sticker
                if len(telegram_set.stickers) == 49:
                    await update.effective_message.reply_text(_('sets.full_warning', user.lang_code))

                chosen_set = user_set
                break

    if chosen_set is None:
        # Create new set
        random_str = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
        name = DEFAULT_VIDEO_SET_NAME % (random_str, context.bot.username)
        new_set_title = _('bot.default_video_set_name', user.lang_code)

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

        # First ever sticker saved
        if Set.select().where(Set.user == user).count() == 1:
            await update.effective_chat.send_message(_('sets.first_set_created', user.lang_code,
                                                       placeholders={'set_name': name, 'set_title': new_set_title}))

        # New sticker set created
        if Set.select().where(Set.user == user).count() > 1:
            await update.effective_chat.send_message(_('sets.new_set_created', user.lang_code,
                                                       placeholders={'set_name': name, 'set_title': new_set_title}))

    else:
        # Add sticker to the existing set
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
