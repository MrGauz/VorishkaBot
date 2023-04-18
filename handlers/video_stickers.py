from telegram import Update, InputSticker
from telegram.ext import ContextTypes

from database.models import SetTypes
from handlers.stickers import save_sticker


async def from_video_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.effective_message.sticker.get_file()
    sticker_bytes = bytes(await file.download_as_bytearray())
    input_sticker = InputSticker(sticker=sticker_bytes, emoji_list=update.effective_message.sticker.emoji)

    await save_sticker(update, context, input_sticker, SetTypes.VIDEO)
