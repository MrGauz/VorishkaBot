from telegram import Update

from database.connection import db
from database.models import User, Set, SetType, SetTypes


def create_tables_and_seed():
    db.connect()
    db.create_tables([User, SetType, Set])

    SetType.get_or_create(name=SetTypes.STATIC.name)
    SetType.get_or_create(name=SetTypes.ANIMATED.name)
    SetType.get_or_create(name=SetTypes.VIDEO.name)
    SetType.get_or_create(name=SetTypes.EMOJI.name)

    db.close()


def get_user(update: Update) -> User:
    db.connect()
    user = User.get_or_none(User.user_id == update.effective_user.id)

    if user is None:
        user = User()
        user.user_id = update.effective_user.id
        user.username = update.effective_user.username
        user.first_name = update.effective_user.first_name
        user.last_name = update.effective_user.last_name
        user.is_premium = update.effective_user.is_premium
        user.language_code = update.effective_user.language_code
        user.save()

    db.close()
    return user
