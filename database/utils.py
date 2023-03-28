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
