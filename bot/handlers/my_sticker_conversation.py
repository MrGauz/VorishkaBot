import json
import logging
import re
from warnings import filterwarnings

from telegram import Update, Sticker, InputSticker
from telegram.error import TelegramError, BadRequest
from telegram.ext import ConversationHandler, CommandHandler, CallbackQueryHandler, MessageHandler, filters, \
    ContextTypes
from telegram.warnings import PTBUserWarning

from bot.bot import personal_sticker_filter
from bot.handlers.commands import cancel_command
from bot.keyboards import get_delete_confirm_keyboard, get_sticker_actions_keyboard, get_set_list_keyboard
from bot.stickers import save_sticker
from database.models import Set, ActionTypes
from database.utils import store_user
from locales import _
from settings import EMOJI_ONLY_REGEX, DEFAULT_STICKER_EMOJI

filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)

logger = logging.getLogger(__name__)

ACTION_SELECTED, CHANGE_EMOJI, MOVE_STICKER, DELETE_STICKER = range(4)


async def start_my_sticker_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = store_user(update)
    sticker = update.effective_message.sticker
    context.user_data.clear()
    context.user_data['selected_sticker'] = sticker.to_json()

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

        case ActionTypes.MOVE_STICKER:
            current_set_name = Sticker.de_json(json.loads(context.user_data['selected_sticker']), context.bot).set_name
            sets_keyboard = await get_set_list_keyboard(user, update.effective_chat, show_new=True,
                                                        hide_name=current_set_name)
            await update.effective_message.edit_text(_('chat.choose_set_move', user.lang_code),
                                                     reply_markup=sets_keyboard)
            return MOVE_STICKER

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

    sticker_id = Sticker.de_json(json.loads(context.user_data['selected_sticker']), context.bot).file_id
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


async def move_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = store_user(update)
    query = update.callback_query
    await query.answer()

    if query.data == ActionTypes.CANCEL:
        return await cancel_command(update, context)

    create_new_pack = query.data == ActionTypes.NEW_SET
    sticker = Sticker.de_json(json.loads(context.user_data['selected_sticker']), context.bot)
    emoji_list = re.compile(EMOJI_ONLY_REGEX).sub('', sticker.emoji) or DEFAULT_STICKER_EMOJI
    file = await sticker.get_file()
    sticker_bytes = bytes(await file.download_as_bytearray())
    input_sticker = InputSticker(sticker_bytes, emoji_list)

    try:
        user_set = await save_sticker(update, context, input_sticker, create_new_pack)
    except TelegramError as e:
        logger.error(f'Error moving sticker {sticker.file_id} for user {user.user_id} ({user.username})',
                     exc_info=e)
        user_set = False

    if user_set:
        await context.bot.delete_sticker_from_set(sticker.file_id)
        await update.effective_message.edit_text(
            _('chat.sticker_moved_success', user.lang_code,
              placeholders={'set_name': user_set.name, 'set_title': user_set.title}))
    else:
        await update.effective_message.edit_text(_('chat.sticker_moved_error', user.lang_code))


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
        MOVE_STICKER: [CallbackQueryHandler(move_sticker)],
        CHANGE_EMOJI: [MessageHandler(filters.TEXT, change_sticker_emoji)],
        DELETE_STICKER: [CallbackQueryHandler(delete_sticker)],
    },
    fallbacks=[CommandHandler('cancel', cancel_command)],
    per_user=True
)
