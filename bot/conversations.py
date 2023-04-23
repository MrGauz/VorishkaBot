from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from database.utils import store_user
from locales import _


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = store_user(update)
    context.user_data.clear()
    await update.message.reply_text(_('commands.cancel', user.lang_code))

    return ConversationHandler.END
