from telegram import Update
from telegram.ext import ContextTypes

from database.utils import get_user


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = await get_user(update)
    # TODO: TRANSLATION
    await context.bot.send_message(user.user_id, "Welcome!")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = await get_user(update)
    # TODO: TRANSLATION
    await context.bot.send_message(user.user_id, "Here is some help")
