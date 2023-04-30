import json
import logging
import re
import tempfile

from telegram import Update, InputSticker
from telegram.ext import ContextTypes

from bot.converters import convert_video
from bot.stickers import save_sticker
from database.utils import store_user
from locales import _
from settings import EMOJI_ONLY_REGEX, DEFAULT_STICKER_EMOJI, MAX_FILE_SIZE

logger = logging.getLogger(__name__)

supported_image_formats = ('image/png', 'image/jpeg', 'image/webp')
supported_video_formats = ('image/gif', 'video/mp4', 'video/webm', 'video/quicktime')


async def from_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = store_user(update)
    document = update.effective_message.document

    # Subscription check
    if not user.is_subscribed() and document.mime_type in supported_video_formats:
        await update.effective_message.reply_text(_('errors.not_subscribed', user.lang_code))
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

    await update.effective_message.reply_text(_("errors.takes_time_warning", user.lang_code))

    emoji_list = tuple(re.compile(EMOJI_ONLY_REGEX).sub('', update.effective_message.caption or '')[:20]
                       or DEFAULT_STICKER_EMOJI)
    filename = tempfile.mktemp(suffix='.' + document.mime_type.split('/')[1])
    file = await document.get_file()

    await file.download_to_drive(filename)
    sticker_path = convert_video(filename)

    if sticker_path is None:
        await update.effective_message.reply_text(_('errors.ffmpeg_failed', user.lang_code))
        return

    input_sticker = InputSticker(sticker=open(sticker_path, 'rb'), emoji_list=emoji_list)
    user_set = await save_sticker(update, context, input_sticker)

    await update.effective_message.reply_text(_('stickers.new_saved', user.lang_code,
                                                placeholders={'set_name': user_set.name, 'set_title': user_set.title}))
