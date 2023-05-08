import logging

from telegram import Update

from database.connection import db
from database.models import User, Set, Transaction, Voucher


def create_tables():
    """
    Create the database tables if they don't exist.
    """
    if db.is_closed():
        db.connect()

    db.create_tables([User, Set, Transaction, Voucher])

    db.close()


def store_user(update: Update) -> User:
    """
    Store the user in the database if they don't exist, or update their information if they do.
    :param update: Update object containing information about the incoming update.
    :return: The user object.
    """
    logger = logging.getLogger(__name__)
    user = User.get_or_none(User.user_id == update.effective_user.id)

    if user is None:
        logger.info(f'Creating new user @{update.effective_user.username} ({update.effective_user.id})')
        user = User()
        user.user_id = update.effective_user.id
        user.lang_code = update.effective_user.language_code

    # Update any fields that might have changed
    user.username = update.effective_user.username
    user.first_name = update.effective_user.first_name
    user.last_name = update.effective_user.last_name
    user.is_premium = update.effective_user.is_premium or False
    if user.is_dirty():
        user.save()

    return user
