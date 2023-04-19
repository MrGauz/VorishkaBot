import logging
import os
import re
import tempfile

import ffmpeg
from telegram import Update, InputSticker
from telegram.ext import ContextTypes

from database.models import SetTypes
from database.utils import get_user
from handlers.stickers import save_sticker
from locales import _
from settings import DEFAULT_NEW_STICKER_EMOJI, EMOJI_ONLY_REGEX

logger = logging.getLogger(__name__)


async def from_video_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.effective_message.sticker.get_file()
    sticker_bytes = bytes(await file.download_as_bytearray())
    input_sticker = InputSticker(sticker=sticker_bytes, emoji_list=update.effective_message.sticker.emoji)

    await save_sticker(update, context, input_sticker, SetTypes.VIDEO)


async def from_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await get_user(update)
    await update.effective_message.reply_text(_("chat.time_warning", user.lang_code))

    mp4_filename = tempfile.mktemp(suffix='.mp4')
    webm_filename = tempfile.mktemp(suffix='.webm')

    file = await update.effective_message.video.get_file()
    await file.download_to_drive(mp4_filename)
    emoji_list = tuple(re.compile(EMOJI_ONLY_REGEX).sub('', update.effective_message.caption or '')
                       or DEFAULT_NEW_STICKER_EMOJI)

    # Get video metadata
    probe = ffmpeg.probe(mp4_filename)
    video_info = next(stream for stream in probe['streams'] if stream['codec_type'] == 'video')
    width = video_info['width']
    height = video_info['height']

    # Calculate new dimensions, keeping aspect ratio and satisfying the size constraint
    new_width = 512 if width >= height else int(width * (512 / height))
    new_height = 512 if width < height else int(height * (512 / width))

    try:
        (ffmpeg
         .input(mp4_filename)
         .filter('scale', new_width, new_height)  # Resize the video
         .filter('loop', '30*3', '0')  # Loop the video for optimal user experience
         .output(
            webm_filename,
            format='webm',
            vcodec='libvpx-vp9',  # VP9 codec
            crf=30,  # Set quality to 30
            r=30,  # Set frame rate to 30 FPS
            an=None,  # Remove audio
            t=3,  # Limit the duration to 3 seconds
         )
         .run(capture_stdout=True, capture_stderr=True)
         )
    except ffmpeg.Error as e:
        logger.error('Failed to process ', e.stderr)
        await update.effective_message.reply_text(_('errors.generic_error', user.lang_code))
        return

    input_sticker = InputSticker(sticker=open(webm_filename, 'rb'), emoji_list=emoji_list)
    await save_sticker(update, context, input_sticker, SetTypes.VIDEO)

    os.remove(mp4_filename)
    os.remove(webm_filename)
