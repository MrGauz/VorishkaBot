from telegram import Update, BotCommand
from telegram._bot import BT
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from database.utils import get_user
from locales import _
from settings import ALL_LANGUAGES


async def set_bot_commands(bot: BT):
    for lang_code in list(ALL_LANGUAGES.keys()):
        await bot.set_my_commands([
            BotCommand(command='rename_set', description=_('bot.rename_set_desc', lang_code)),
            BotCommand(command='delete_set', description=_('bot.rename_set_desc', lang_code)),
            BotCommand(command='translate', description=_('bot.translate_desc', lang_code)),
            BotCommand(command='help', description=_('bot.help_decs', lang_code))
        ], language_code=lang_code)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = await get_user(update)
    await context.bot.send_message(user.user_id, _("commands.start", user.lang_code), parse_mode=ParseMode.HTML)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = await get_user(update)
    await context.bot.send_message(user.user_id, _("commands.help", user.lang_code), parse_mode=ParseMode.HTML)
