from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Chat

from database.models import Set, SetTypes, User
from settings import ANIMATED_SET_EMOJI, EMOJI_SET_EMOJI
from locales import _


async def get_set_selection_buttons(user: User, chat: Chat) -> InlineKeyboardMarkup | None:
    sets = Set.select().where(Set.user == user).order_by(Set.set_type.desc())

    if not sets:
        await chat.send_message(_('errors.no_sets', user.lang_code))
        return None

    buttons = []
    for telegram_set in sets:
        match telegram_set.set_type:
            case SetTypes.EMOJI:
                emoji = EMOJI_SET_EMOJI
            case SetTypes.ANIMATED | SetTypes.VIDEO | _:
                emoji = ANIMATED_SET_EMOJI
        buttons.append([InlineKeyboardButton(f'{emoji} {telegram_set.title}', callback_data=telegram_set.name)])
    buttons.append([InlineKeyboardButton(_('buttons.cancel', user.lang_code), callback_data='cancel')])

    return InlineKeyboardMarkup(buttons)
