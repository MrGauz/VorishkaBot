import json
import logging
import tempfile

import emojis
from telegram import Update, InputSticker
from telegram.constants import ChatAction, StickerLimit
from telegram.ext import ContextTypes

from bot.converters import convert_video
from bot.stickers import save_sticker
from database.models import AnalyticsTypes
from database.utils import store_user, new_analytics_event
from locales import _
from settings import DEFAULT_STICKER_EMOJI, MAX_FILE_SIZE

logger = logging.getLogger(__name__)

supported_image_formats = ('image/png', 'image/jpeg', 'image/webp')
supported_video_formats = ('image/gif', 'video/mp4', 'video/webm', 'video/quicktime')


async def from_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler for converting a document to a video sticker and saving it.

    :param update: Update object containing information about the incoming update.
    :param context: Callback context which contains information about the current state of the bot.
    """
    await update.effective_chat.send_action(ChatAction.TYPING)
    user = store_user(update)
    document = update.effective_message.document

    # Subscription check
    if not user.is_subscribed() and document.mime_type in supported_video_formats:
        await update.effective_message.reply_text(_('errors.not_subscribed', user.lang_code))
        new_analytics_event(AnalyticsTypes.NOT_SUBSCRIBED_ERROR, update, user)
        return

    # Filter out unsupported file types
    if document.mime_type not in supported_image_formats + supported_video_formats:
        logger.warning(f'Received unknown document type: {update.message.document.mime_type}\n'
                       f'update={json.dumps(update.to_dict())}')
        await update.effective_message.reply_text(_('errors.unknown_document_type', user.lang_code))
        return

    if document.file_size > MAX_FILE_SIZE:
        await update.effective_message.reply_text(_('errors.file_too_big', user.lang_code))
        return

    await update.effective_message.reply_text(_('errors.takes_time_warning', user.lang_code))

    if document.mime_type in supported_image_formats:
        await update.effective_chat.send_action(ChatAction.UPLOAD_PHOTO)
    else:
        await update.effective_chat.send_action(ChatAction.UPLOAD_VIDEO)
    emoji = tuple(emojis.get(update.effective_message.caption or ''))[
            :StickerLimit.MAX_STICKER_EMOJI] or DEFAULT_STICKER_EMOJI
    filename = tempfile.mktemp(suffix='.' + document.mime_type.split('/')[1])
    file = await document.get_file()

    await file.download_to_drive(filename)
    sticker_path = await convert_video(filename)

    if sticker_path is None:
        await update.effective_chat.send_action(ChatAction.TYPING)
        await update.effective_message.reply_text(_('errors.ffmpeg_failed', user.lang_code))
        return

    input_sticker = InputSticker(sticker=open(sticker_path, 'rb'), emoji_list=emoji)
    user_set = await save_sticker(update, context, input_sticker)

    if user_set:
        await update.effective_chat.send_action(ChatAction.TYPING)
        await update.effective_message.reply_text(_('stickers.new_saved', user.lang_code,
                                                    placeholders={'set_name': user_set.name,
                                                                  'set_title': user_set.title,
                                                                  'emoji': ''.join(emoji)}))
        new_analytics_event(AnalyticsTypes.NEW_STICKER_FROM_FILE, update, user)
