from telegram import Update
from telegram.ext import ContextTypes

from database.utils import get_user
from locales import _


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = await get_user(update)
    await context.bot.send_message(user.user_id, _("chat.welcome", user.lang_code))


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = await get_user(update)
    await context.bot.send_message(user.user_id, _("chat.help", user.lang_code))
