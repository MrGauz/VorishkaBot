from warnings import filterwarnings

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import ConversationHandler, CommandHandler, ContextTypes, CallbackQueryHandler
from telegram.warnings import PTBUserWarning

from database.utils import get_user, change_user_language
from handlers.conversations import cancel_command
from locales import _

filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)

LANGUAGE_CHOICE = 0


async def translate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await get_user(update)
    await context.bot.send_message(
        update.effective_user.id,
        'Choose language',
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton('\U0001f1ec\U0001f1e7', callback_data='en'),
                InlineKeyboardButton('\U0001f1f7\U0001f1fa', callback_data='ru'),
            ],
            [
                InlineKeyboardButton(_('buttons.cancel', user.lang_code), callback_data='cancel'),
            ]
        ])
    )
    return LANGUAGE_CHOICE


async def language_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await get_user(update)
    query = update.callback_query
    await query.answer()

    if query.data == 'cancel':
        await update.effective_message.reply_text(_('commands.cancel', user.lang_code), parse_mode=ParseMode.HTML)
        return ConversationHandler.END

    await change_user_language(user.user_id, query.data)
    await update.effective_message.reply_text(_('chat.language_changed', query.data), parse_mode=ParseMode.HTML)

    return ConversationHandler.END


translate_conversation = ConversationHandler(
    entry_points=[CommandHandler('translate', translate_command)],
    states={
        LANGUAGE_CHOICE: [CallbackQueryHandler(language_selected)],
    },
    fallbacks=[CommandHandler('cancel', cancel_command)],
    per_user=True
)
