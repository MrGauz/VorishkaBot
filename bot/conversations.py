from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler

from database.utils import get_user
from locales import _


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update)
    context.user_data.clear()
    await update.message.reply_text(_('commands.cancel', user.lang_code), parse_mode=ParseMode.HTML)

    return ConversationHandler.END
