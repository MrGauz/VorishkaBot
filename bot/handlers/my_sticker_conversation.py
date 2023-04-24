import logging
import re
from warnings import filterwarnings

from telegram import Update
from telegram.error import TelegramError, BadRequest
from telegram.ext import ConversationHandler, CommandHandler, CallbackQueryHandler, MessageHandler, filters, \
    ContextTypes
from telegram.warnings import PTBUserWarning

from bot.bot import personal_sticker_filter
from bot.handlers.commands import cancel_command
from bot.keyboards import get_delete_confirm_keyboard, get_sticker_actions_keyboard
from database.models import Set, ActionTypes
from database.utils import store_user
from locales import _
from settings import EMOJI_ONLY_REGEX

filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)

logger = logging.getLogger(__name__)

ACTION_SELECTED, CHANGE_EMOJI, DELETE_STICKER = range(3)


async def start_my_sticker_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = store_user(update)
    sticker = update.effective_message.sticker
    context.user_data.clear()
    context.user_data['selected_sticker_id'] = sticker.file_id

    user_set = Set.get(Set.user_id == user.id, Set.name == sticker.set_name)
    actions_keyboard = get_sticker_actions_keyboard(user)
    await update.message.reply_text(
        _('chat.sticker_summary_message', user.lang_code,
          placeholders={'emoji': sticker.emoji, 'set_name': user_set.name, 'set_title': user_set.title}),
        reply_markup=actions_keyboard)

    return ACTION_SELECTED


async def sticker_action_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = store_user(update)
    query = update.callback_query
    await query.answer()

    match query.data:
        case ActionTypes.CHANGE_EMOJI:
            await update.effective_message.edit_text(_('chat.choose_new_sticker_emoji', user.lang_code),
                                                     reply_markup=None)
            return CHANGE_EMOJI

        case ActionTypes.DELETE_STICKER:
            confirm_keyboard = get_delete_confirm_keyboard(user, is_sticker=True)
            await update.effective_message.edit_text(text=_('chat.confirm_delete_sticker', user.lang_code),
                                                     reply_markup=confirm_keyboard)
            return DELETE_STICKER

        case ActionTypes.CANCEL | _:
            return await cancel_command(update, context)


async def change_sticker_emoji(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = store_user(update)
    text = update.effective_message.text

    if text == '/' + ActionTypes.CANCEL:
        return await cancel_command(update, context)

    emoji = tuple(set(re.compile(EMOJI_ONLY_REGEX).sub('', text)[:20]))
    if not emoji:
        await update.effective_message.reply_text(_('chat.emoji_invalid', user.lang_code))
        return CHANGE_EMOJI

    sticker_id = context.user_data['selected_sticker_id']
    try:
        result = await context.bot.set_sticker_emoji_list(sticker_id, emoji)
    except TelegramError as e:
        logger.error(f'Error changing emoji {emoji} for sticker {sticker_id} for user {user.user_id} ({user.username})',
                     exc_info=e)
        result = False

    if result:
        await update.effective_message.reply_text(_('chat.emoji_change_success', user.lang_code,
                                                    placeholders={'new_emoji': ''.join(emoji)}))
    else:
        await update.effective_message.reply_text(_('chat.emoji_change_error', user.lang_code))

    return ConversationHandler.END


async def delete_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = store_user(update)
    query = update.callback_query
    await query.answer()

    if query.data != ActionTypes.DELETE_STICKER:
        return await cancel_command(update, context)

    sticker_id = context.user_data['selected_sticker_id']
    try:
        result = await context.bot.delete_sticker_from_set(sticker_id)
    except BadRequest as e:
        logger.error(f'Error deleting sticker {sticker_id} for user {user.user_id} ({user.username})', exc_info=e)
        result = False

    if result:
        await update.effective_message.edit_text(_('chat.sticker_deleted_success', user.lang_code))
    else:
        await update.effective_message.edit_text(_('chat.sticker_deleted_error', user.lang_code))

    context.user_data.clear()
    return ConversationHandler.END


my_sticker_conversation = ConversationHandler(
    entry_points=[MessageHandler(personal_sticker_filter, start_my_sticker_conversation)],
    states={
        ACTION_SELECTED: [CallbackQueryHandler(sticker_action_selected)],
        CHANGE_EMOJI: [MessageHandler(filters.TEXT, change_sticker_emoji)],
        DELETE_STICKER: [CallbackQueryHandler(delete_sticker)],
    },
    fallbacks=[CommandHandler('cancel', cancel_command)],
    per_user=True
)
