import logging
from warnings import filterwarnings

from telegram import Update
from telegram.error import TelegramError
from telegram.ext import ConversationHandler, CommandHandler, CallbackQueryHandler, MessageHandler, filters, \
    ContextTypes
from telegram.warnings import PTBUserWarning

from bot.sets import get_set_selection_buttons
from database.models import Set
from database.utils import store_user
from bot.conversations import cancel_command
from locales import _

filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)

logger = logging.getLogger(__name__)

SELECT_SET, RENAME_SET = range(2)


async def start_rename_set_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = store_user(update)
    context.user_data.clear()

    keyboard = await get_set_selection_buttons(user, update.effective_chat)
    if not keyboard:
        return ConversationHandler.END

    await update.message.reply_text(_('chat.choose_set_rename', user.lang_code), reply_markup=keyboard)

    return SELECT_SET


async def sticker_set_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = store_user(update)
    query = update.callback_query
    await query.answer()

    if query.data == 'cancel':
        await update.effective_message.reply_text(_('commands.cancel', user.lang_code))
        return ConversationHandler.END

    context.user_data['selected_set'] = query.data
    await context.bot.send_message(user.user_id, _('chat.choose_new_set_name', user.lang_code))

    return RENAME_SET


async def new_set_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = store_user(update)
    text = update.effective_message.text
    set_name = context.user_data['selected_set']

    if text == '/cancel':
        await update.effective_message.reply_text(_('commands.cancel', user.lang_code))
        return ConversationHandler.END

    try:
        result = await context.bot.set_sticker_set_title(set_name, text)
    except TelegramError as e:
        logger.error(f'Error renaming set {set_name}', exc_info=e)
        result = False

    if result:
        await context.bot.send_message(user.user_id, _('chat.set_renamed_success', user.lang_code,
                                                       {'set_name': set_name, 'new_title': text}))

        sticker_set = Set.get(Set.name == set_name)
        sticker_set.title = text.strip()
        sticker_set.save()
    else:
        await context.bot.send_message(user.user_id, _('chat.set_renamed_error', user.lang_code, {'new_name': text}))

    context.user_data.clear()
    return ConversationHandler.END


rename_set_command = ConversationHandler(
    entry_points=[CommandHandler('rename_set', start_rename_set_command)],
    states={
        SELECT_SET: [CallbackQueryHandler(sticker_set_selected)],
        RENAME_SET: [MessageHandler(filters.TEXT, new_set_name)],
    },
    fallbacks=[CommandHandler('cancel', cancel_command)],
    per_user=True
)
