import json

from telegram import Update

from database.connection import db
from database.models import User, Set, Transaction, Voucher, Analytics, AnalyticsTypes


def create_tables():
    """
    Create the database tables if they don't exist.
    """
    if db.is_closed():
        db.connect()

    db.create_tables([User, Set, Transaction, Voucher, Analytics])

    db.close()


def store_user(update: Update) -> User:
    """
    Store the user in the database if they don't exist, or update their information if they do.
    :param update: Update object containing information about the incoming update.
    :return: The user object.
    """
    user = User.get_or_none(User.user_id == update.effective_user.id)

    is_new_user = False
    if user is None:
        # New user
        user = User()
        user.user_id = update.effective_user.id
        user.lang_code = update.effective_user.language_code
        is_new_user = True

    # Update any fields that might have changed
    user.username = update.effective_user.username
    user.first_name = update.effective_user.first_name
    user.last_name = update.effective_user.last_name
    user.is_premium = update.effective_user.is_premium or False
    if user.is_dirty():
        user.save()

    if is_new_user:
        new_analytics_event(AnalyticsTypes.NEW_USER, update, user)

    return user


def new_analytics_event(action_type: AnalyticsTypes, update: Update, user: User) -> None:
    """
    Create a new analytics entry.

    :param action_type: The type of action to be recorded.
    :param update: The incoming update.
    :param user: The user that triggered the action.
    :return: None
    """
    analytics = Analytics(action_type=action_type, user=user, update=json.dumps(update.to_dict()))
    analytics.save()
