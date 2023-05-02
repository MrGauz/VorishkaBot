from warnings import filterwarnings

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ChatAction
from telegram.ext import ConversationHandler, CommandHandler, ContextTypes, CallbackQueryHandler
from telegram.warnings import PTBUserWarning

from bot.handlers.commands import cancel_command
from database.utils import store_user
from locales import _
from settings import ALL_LANGUAGES

filterwarnings(action='ignore', message=r'.*CallbackQueryHandler', category=PTBUserWarning)

LANGUAGE_CHOICE = 0


async def start_translate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Starts the 'translate' conversation.

    :param update: Update object containing information about the incoming update.
    :param context: Callback context which contains information about the current state of the bot.
    """
    await update.effective_chat.send_action(ChatAction.TYPING)
    user = store_user(update)
    await context.bot.send_message(
        update.effective_user.id,
        _('bot.choose_language', user.lang_code),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(v, callback_data=k) for k, v in ALL_LANGUAGES.items()],
            [InlineKeyboardButton(_('keyboards.cancel', user.lang_code), callback_data='cancel')]
        ])
    )
    return LANGUAGE_CHOICE


async def language_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler for selecting a language.

    :param update: Update object containing information about the incoming update.
    :param context: Callback context which contains information about the current state of the bot.
    """
    user = store_user(update)
    query = update.callback_query
    await query.answer()

    await update.effective_chat.send_action(ChatAction.TYPING)
    if query.data == 'cancel':
        await update.effective_message.reply_text(_('bot.cancel_command', user.lang_code))
        return ConversationHandler.END

    user.lang_code = query.data
    user.save()
    await update.effective_message.reply_text(_('bot.language_changed', query.data))

    return ConversationHandler.END


translate_command = ConversationHandler(
    entry_points=[CommandHandler('translate', start_translate_command)],
    states={
        LANGUAGE_CHOICE: [CallbackQueryHandler(language_selected)],
    },
    fallbacks=[CommandHandler('cancel', cancel_command)],
    per_user=True
)
