from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from database.utils import store_user
from locales import _


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = store_user(update)
    await update.message.reply_text(_("bot.start_command", user.lang_code))


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = store_user(update)
    await update.message.reply_text(_("bot.help_command", user.lang_code))


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = store_user(update)
    context.user_data.clear()
    if update.effective_message.from_user.username == context.bot.username:
        await update.effective_message.edit_text(_('bot.cancel_command', user.lang_code), reply_markup=None)
    else:
        await update.effective_message.reply_text(_('bot.cancel_command', user.lang_code), reply_markup=None)

    return ConversationHandler.END
