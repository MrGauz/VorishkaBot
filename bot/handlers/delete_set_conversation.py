import logging
from warnings import filterwarnings

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram.ext import ConversationHandler, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.warnings import PTBUserWarning

from bot.sets import get_set_selection_buttons
from database.models import Set
from database.utils import get_user
from bot.conversations import cancel_command
from locales import _

filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)

logger = logging.getLogger(__name__)

SELECT_SET, DELETE_SET = range(2)


async def start_delete_set_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await get_user(update)
    context.user_data.clear()

    keyboard = await get_set_selection_buttons(user, update.effective_chat)
    if not keyboard:
        return ConversationHandler.END

    await update.message.reply_text(_('chat.choose_set_delete', user.lang_code), parse_mode=ParseMode.HTML,
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

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(_('buttons.delete_set_no', user.lang_code), callback_data='cancel')],
        [InlineKeyboardButton(_('buttons.delete_set_nope', user.lang_code), callback_data='cancel')],
        [InlineKeyboardButton(_('buttons.delete_set_yes', user.lang_code), callback_data='delete')]
    ])

    telegram_set: Set = Set.get(user=user, name=query.data)
    await update.callback_query.message.edit_text(
        _('chat.confirm_delete_set', user.lang_code, {'set_name': telegram_set.name, 'set_title': telegram_set.title}),
        parse_mode=ParseMode.HTML, reply_markup=keyboard)

    return DELETE_SET


async def delete_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await get_user(update)
    query = update.callback_query
    await query.answer()

    if query.data == 'cancel':
        await update.effective_message.reply_text(_('commands.cancel', user.lang_code), parse_mode=ParseMode.HTML)
        return ConversationHandler.END

    telegram_set: Set = Set.get(user=user, name=context.user_data['selected_set'])
    try:
        result = await context.bot.delete_sticker_set(telegram_set.name)
    except BadRequest as e:
        logger.error(f'Error deleting set {telegram_set.name} for user {user.user_id} ({user.username})', exc_info=e)
        result = False
    await update.effective_message.delete()

    if result:
        await context.bot.send_message(user.user_id,
                                       _('chat.set_deleted_success', user.lang_code, {'set_title': telegram_set.title}),
                                       parse_mode=ParseMode.HTML)
        telegram_set.delete_instance()
    else:
        await context.bot.send_message(user.user_id,
                                       _('chat.set_deleted_error', user.lang_code, {'set_title': telegram_set.title}),
                                       parse_mode=ParseMode.HTML)

    context.user_data.clear()
    return ConversationHandler.END


delete_set_command = ConversationHandler(
    entry_points=[CommandHandler('delete_set', start_delete_set_command)],
    states={
        SELECT_SET: [CallbackQueryHandler(sticker_set_selected)],
        DELETE_SET: [CallbackQueryHandler(delete_set)],
    },
    fallbacks=[CommandHandler('cancel', cancel_command)],
    per_user=True
)
