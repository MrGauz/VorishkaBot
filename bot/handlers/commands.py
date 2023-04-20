from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from database.utils import get_user
from locales import _


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = get_user(update)
    await context.bot.send_message(user.user_id, _("commands.start", user.lang_code), parse_mode=ParseMode.HTML)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = get_user(update)
    await context.bot.send_message(user.user_id, _("commands.help", user.lang_code), parse_mode=ParseMode.HTML)
