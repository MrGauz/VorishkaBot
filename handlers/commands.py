from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from database.models import SetTypes, Actions
from database.utils import get_user, get_user_sets
from locales import _
from settings import STATIC_SET_EMOJI, ANIMATED_SET_EMOJI, EMOJI_SET_EMOJI


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = await get_user(update)
    await context.bot.send_message(user.user_id, _("chat.welcome", user.lang_code), parse_mode=ParseMode.HTML)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = await get_user(update)
    await context.bot.send_message(user.user_id, _("chat.help", user.lang_code), parse_mode=ParseMode.HTML)


async def rename_set_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = await get_user(update)
    sets = await get_user_sets(user)
    context.user_data.clear()
    context.user_data['action'] = Actions.RENAME_SET

    buttons = []
    for telegram_set in sets:
        match telegram_set.set_type:
            case SetTypes.ANIMATED | SetTypes.VIDEO:
                emoji = ANIMATED_SET_EMOJI
            case SetTypes.EMOJI:
                emoji = EMOJI_SET_EMOJI
            case SetTypes.STATIC | _:
                emoji = STATIC_SET_EMOJI

        buttons.append(InlineKeyboardButton(f'{emoji} {telegram_set.title}', callback_data=telegram_set.name))
    keyboard = InlineKeyboardMarkup([buttons])

    await context.bot.send_message(user.user_id, _('chat.choose_set', user.lang_code), parse_mode=ParseMode.HTML,
                                   reply_markup=keyboard)
