from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Chat

from database.models import Set, SetTypes, User, ActionTypes
from settings import VIDEO_SET_EMOJI, EMOJI_SET_EMOJI
from locales import _


async def get_set_list_keyboard(user: User, show_new=False, hide_name: str = None) -> InlineKeyboardMarkup | None:
    sets = Set.select().where(Set.user == user).order_by(Set.set_type.desc())

    if not sets:
        return None

    buttons = []
    if show_new:
        buttons.append([InlineKeyboardButton(_('keyboards.new_set', user.lang_code), callback_data=ActionTypes.NEW_SET)])
    for telegram_set in sets:
        match telegram_set.set_type:
            case SetTypes.EMOJI:
                emoji = EMOJI_SET_EMOJI
            case SetTypes.VIDEO | _:
                emoji = VIDEO_SET_EMOJI
        if telegram_set.name == hide_name:
            continue
        buttons.append([InlineKeyboardButton(f'{emoji} {telegram_set.title}', callback_data=telegram_set.name)])
    buttons.append([InlineKeyboardButton(_('keyboards.cancel', user.lang_code), callback_data=ActionTypes.CANCEL)])

    return InlineKeyboardMarkup(buttons)


def get_set_actions_keyboard(user: User) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(_('keyboards.rename_set', user.lang_code), callback_data=ActionTypes.RENAME_SET)],
        [InlineKeyboardButton(_('keyboards.delete_set', user.lang_code), callback_data=ActionTypes.DELETE_SET)],
        [InlineKeyboardButton(_('keyboards.cancel', user.lang_code), callback_data=ActionTypes.CANCEL)]
    ])


def get_delete_confirm_keyboard(user: User, is_sticker=False) -> InlineKeyboardMarkup:
    delete_action = ActionTypes.DELETE_STICKER if is_sticker else ActionTypes.DELETE_SET
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(_('keyboards.delete_set_no', user.lang_code), callback_data=ActionTypes.CANCEL)],
        [InlineKeyboardButton(_('keyboards.delete_set_nope', user.lang_code), callback_data=ActionTypes.CANCEL)],
        [InlineKeyboardButton(_('keyboards.delete_set_yes', user.lang_code), callback_data=delete_action)]
    ])


def get_sticker_actions_keyboard(user: User) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(_('keyboards.change_emoji', user.lang_code), callback_data=ActionTypes.CHANGE_EMOJI)],
        [InlineKeyboardButton(_('keyboards.move_sticker', user.lang_code), callback_data=ActionTypes.MOVE_STICKER)],
        [InlineKeyboardButton(_('keyboards.delete_sticker', user.lang_code), callback_data=ActionTypes.DELETE_STICKER)],
        [InlineKeyboardButton(_('keyboards.cancel', user.lang_code), callback_data=ActionTypes.CANCEL)]
    ])
