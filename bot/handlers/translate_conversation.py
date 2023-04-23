from warnings import filterwarnings

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ConversationHandler, CommandHandler, ContextTypes, CallbackQueryHandler
from telegram.warnings import PTBUserWarning

from database.utils import store_user
from bot.conversations import cancel_command
from locales import _
from settings import ALL_LANGUAGES

filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)

LANGUAGE_CHOICE = 0


async def start_translate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = store_user(update)
    await context.bot.send_message(
        update.effective_user.id,
        'Choose language',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(v, callback_data=k) for k, v in ALL_LANGUAGES.items()],
            [InlineKeyboardButton(_('buttons.cancel', user.lang_code), callback_data='cancel')]
        ])
    )
    return LANGUAGE_CHOICE


async def language_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = store_user(update)
    query = update.callback_query
    await query.answer()

    if query.data == 'cancel':
        await update.effective_message.reply_text(_('commands.cancel', user.lang_code))
        return ConversationHandler.END

    user.lang_code = query.data
    user.save()
    await update.effective_message.reply_text(_('chat.language_changed', query.data))

    return ConversationHandler.END


translate_command = ConversationHandler(
    entry_points=[CommandHandler('translate', start_translate_command)],
    states={
        LANGUAGE_CHOICE: [CallbackQueryHandler(language_selected)],
    },
    fallbacks=[CommandHandler('cancel', cancel_command)],
    per_user=True
)
