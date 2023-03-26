from telegram import Update
from telegram.ext import ContextTypes

from database import user_exists, create_user


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not user_exists(update.effective_user.id):
        user = update.effective_user
        create_user(user.id, user.username, user.first_name, user.last_name, user.language_code, user.is_premium)
