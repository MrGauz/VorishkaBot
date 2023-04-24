import logging
from warnings import filterwarnings

from telegram import Update
from telegram.error import TelegramError, BadRequest
from telegram.ext import ConversationHandler, CommandHandler, CallbackQueryHandler, MessageHandler, filters, \
    ContextTypes
from telegram.warnings import PTBUserWarning

from bot.handlers.commands import cancel_command
from bot.keyboards import get_set_list_keyboard, get_set_actions_keyboard, get_delete_confirm_keyboard
from database.models import Set, ActionTypes
from database.utils import store_user
from locales import _

filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)

logger = logging.getLogger(__name__)

SET_SELECTED, ACTION_SELECTED, RENAME_SET, DELETE_SET = range(4)


async def start_my_sets_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = store_user(update)
    context.user_data.clear()

    keyboard = await get_set_list_keyboard(user, update.effective_chat)
    if not keyboard:
        return ConversationHandler.END

    await update.message.reply_text(_('chat.choose_set_rename', user.lang_code), reply_markup=keyboard)

    return SET_SELECTED


async def set_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = store_user(update)
    query = update.callback_query
    context.user_data['selected_set'] = query.data
    await query.answer()

    if query.data == ActionTypes.CANCEL:
        return await cancel_command(update, context)

    telegram_set = await context.bot.get_sticker_set(query.data)
    placeholders = {
        'set_title': telegram_set.title,
        'set_name': telegram_set.name,
        'sticker_count': len(telegram_set.stickers)
    }
    actions_keyboard = get_set_actions_keyboard(user)
    await update.effective_message.edit_text(_('chat.set_summary_message', user.lang_code, placeholders=placeholders),
                                             reply_markup=actions_keyboard)

    return ACTION_SELECTED


async def set_action_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = store_user(update)
    query = update.callback_query
    context.user_data['selected_action'] = query.data
    await query.answer()

    match query.data:
        case ActionTypes.RENAME_SET:
            await update.effective_message.edit_text(_('chat.choose_new_set_name', user.lang_code), reply_markup=None)
            return RENAME_SET

        case ActionTypes.DELETE_SET:
            confirm_keyboard = get_delete_confirm_keyboard(user)
            telegram_set: Set = Set.get(user=user, name=context.user_data['selected_set'])
            await update.effective_message.edit_text(
                text=_('chat.confirm_delete_set', user.lang_code,
                       placeholders={'set_name': telegram_set.name, 'set_title': telegram_set.title}),
                reply_markup=confirm_keyboard)
            return DELETE_SET

        case ActionTypes.CANCEL | _:
            return await cancel_command(update, context)


async def rename_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = store_user(update)
    text = update.effective_message.text[:64]
    set_name = context.user_data['selected_set']

    if text == '/' + ActionTypes.CANCEL:
        return await cancel_command(update, context)

    try:
        result = await context.bot.set_sticker_set_title(set_name, text)
    except TelegramError as e:
        logger.error(f'Error renaming set {set_name}', exc_info=e)
        result = False

    if result:
        await update.effective_message.reply_text(_('chat.set_renamed_success', user.lang_code,
                                                    {'set_name': set_name, 'new_title': text}))

        sticker_set = Set.get(Set.name == set_name)
        sticker_set.title = text.strip()
        sticker_set.save()
    else:
        await update.effective_message.reply_text(_('chat.set_renamed_error', user.lang_code, {'new_name': text}))

    context.user_data.clear()
    return ConversationHandler.END


async def delete_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = store_user(update)
    query = update.callback_query
    await query.answer()

    if query.data != ActionTypes.DELETE_SET:
        return await cancel_command(update, context)

    telegram_set: Set = Set.get(user=user, name=context.user_data['selected_set'])
    try:
        result = await context.bot.delete_sticker_set(telegram_set.name)
    except BadRequest as e:
        logger.error(f'Error deleting set {telegram_set.name} for user {user.user_id} ({user.username})', exc_info=e)
        result = False

    if result:
        await update.effective_message.edit_text(_('chat.set_deleted_success', user.lang_code,
                                                   placeholders={'set_title': telegram_set.title}))
        telegram_set.delete_instance()
    else:
        await update.effective_message.edit_text(_('chat.set_deleted_error', user.lang_code,
                                                   placeholders={'set_title': telegram_set.title}))

    context.user_data.clear()
    return ConversationHandler.END


my_sets_command = ConversationHandler(
    entry_points=[CommandHandler('my_sets', start_my_sets_command)],
    states={
        SET_SELECTED: [CallbackQueryHandler(set_selected)],
        ACTION_SELECTED: [CallbackQueryHandler(set_action_selected)],
        RENAME_SET: [MessageHandler(filters.TEXT, rename_set)],
        DELETE_SET: [CallbackQueryHandler(delete_set)],
    },
    fallbacks=[CommandHandler('cancel', cancel_command)],
    per_user=True
)
