from telegram import Update
from telegram.ext import ContextTypes

from database.utils import get_user


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = get_user(update)

    # TODO: send actual welcome message
    await context.bot.send_message(user.user_id, "Welcome!")
