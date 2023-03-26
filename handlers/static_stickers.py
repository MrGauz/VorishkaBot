import logging

from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def save_static_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    file = await update.message.sticker.get_file()
    logger.info("file_path: " + file.file_path)
    # await file.download_to_drive('.\images\' + file.file_unique_id)
