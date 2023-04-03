import logging

from telegram import Update

from database.connection import db
from database.models import User, Set, SetTypes

logger = logging.getLogger(__name__)


def create_tables():
    if db.is_closed():
        db.connect()

    db.create_tables([User, Set])

    db.close()


async def get_user(update: Update) -> User:
    if db.is_closed():
        db.connect()

    user = User.get_or_none(User.user_id == update.effective_user.id)

    if user is None:
        logger.info(f"Creating new user @{update.effective_user.username} ({update.effective_user.id})")
        user = User()
        user.user_id = update.effective_user.id

    # Update any fields that might have changed
    user.username = update.effective_user.username
    user.first_name = update.effective_user.first_name
    user.last_name = update.effective_user.last_name
    user.is_premium = update.effective_user.is_premium
    user.language_code = update.effective_user.language_code
    if user.is_dirty():
        user.save()

    db.close()
    return user


async def save_new_set(user: User, name: str, title: str, set_type: SetTypes) -> Set:
    logger.info(f"Creating new sticker set for @{user.username}: {name}")

    if db.is_closed():
        db.connect()
    stickers_set = Set()
    stickers_set.user = user
    stickers_set.name = name
    stickers_set.title = title
    stickers_set.set_type = set_type
    stickers_set.save()
    db.close()

    return stickers_set
