import json
import logging
import re
import tempfile

from telegram import Update, InputSticker
from telegram.ext import ContextTypes

from bot.converters import convert_video
from bot.stickers import save_sticker
from database.models import SetTypes
from database.utils import store_user
from locales import _
from settings import EMOJI_ONLY_REGEX, DEFAULT_NEW_STICKER_EMOJI, MAX_FILE_SIZE

logger = logging.getLogger(__name__)


async def from_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = store_user(update)

    emoji_list = tuple(re.compile(EMOJI_ONLY_REGEX).sub('', update.effective_message.caption or '')
                       or DEFAULT_NEW_STICKER_EMOJI)

    match update.effective_message.document.mime_type:
        case 'image/png' | 'image/jpeg' | 'image/webp' | 'image/gif' | 'video/mp4' | 'video/webm' | 'video/quicktime':
            if update.effective_message.document.file_size > MAX_FILE_SIZE:
                await update.effective_message.reply_text(_('errors.file_too_big', user.lang_code))
                return

            await update.effective_message.reply_text(_("chat.time_warning", user.lang_code))

            filename = tempfile.mktemp(suffix='.' + update.effective_message.document.mime_type.split('/')[1])
            file = await update.effective_message.document.get_file()

            await file.download_to_drive(filename)
            sticker_path = convert_video(filename)

            if sticker_path is None:
                await update.effective_message.reply_text(_('errors.ffmpeg_error', user.lang_code))
                return

            input_sticker = InputSticker(sticker=open(sticker_path, 'rb'), emoji_list=emoji_list)
            await save_sticker(update, context, input_sticker, SetTypes.VIDEO)

        case _:
            logger.warning(f'Received unknown document type: {update.message.document.mime_type}\n'
                           f'update={json.dumps(update.to_dict())}')
            await update.effective_message.reply_text(_('errors.unknown_document_type', user.lang_code))
