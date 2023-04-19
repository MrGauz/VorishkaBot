from warnings import filterwarnings

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ConversationHandler, CommandHandler, CallbackQueryHandler, MessageHandler, filters, \
    ContextTypes
from telegram.warnings import PTBUserWarning

from bot.set_utils import get_set_selection_buttons
from database.utils import get_user, rename_set
from handlers.conversations import cancel_command
from locales import _

filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)

SELECT_SET, RENAME_SET = range(2)


async def rename_set_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await get_user(update)
    context.user_data.clear()

    keyboard = await get_set_selection_buttons(user, update.effective_chat)
    if not keyboard:
        return ConversationHandler.END

    await update.message.reply_text(_('chat.choose_set_rename', user.lang_code), parse_mode=ParseMode.HTML,
                                    reply_markup=keyboard)

    return SELECT_SET


async def sticker_set_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await get_user(update)
    query = update.callback_query
    await query.answer()

    if query.data == 'cancel':
        await update.effective_message.reply_text(_('commands.cancel', user.lang_code), parse_mode=ParseMode.HTML)
        return ConversationHandler.END

    context.user_data['selected_set'] = query.data
    await context.bot.send_message(user.user_id, _('chat.choose_new_set_name', user.lang_code),
                                   parse_mode=ParseMode.HTML)

    return RENAME_SET


async def new_set_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await get_user(update)
    text = update.effective_message.text
    set_name = context.user_data['selected_set']

    if text == '/cancel':
        await update.effective_message.reply_text(_('commands.cancel', user.lang_code), parse_mode=ParseMode.HTML)
        return ConversationHandler.END

    result = await context.bot.set_sticker_set_title(set_name, text)
    if result:
        await context.bot.send_message(user.user_id, _('chat.set_renamed_success', user.lang_code,
                                                       {'set_name': set_name, 'new_title': text}),
                                       parse_mode=ParseMode.HTML)
        await rename_set(set_name, text)
    else:
        await context.bot.send_message(user.user_id, _('chat.set_renamed_error', user.lang_code, {'new_name': text}),
                                       parse_mode=ParseMode.HTML)

    context.user_data.clear()
    return ConversationHandler.END


rename_set_conversation = ConversationHandler(
    entry_points=[CommandHandler('rename_set', rename_set_command)],
    states={
        SELECT_SET: [CallbackQueryHandler(sticker_set_selected)],
        RENAME_SET: [MessageHandler(filters.TEXT, new_set_name)],
    },
    fallbacks=[CommandHandler('cancel', cancel_command)],
    per_user=True
)
