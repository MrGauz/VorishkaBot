from datetime import datetime
from enum import Enum

from peewee import Model, BigIntegerField, CharField, BooleanField, DateTimeField, ForeignKeyField

from database.connection import db


class CharEnum(str, Enum):
    """A custom Enum subclass that inherits from both str and Enum,
    so that the enum members are automatically converted to strings."""

    def _generate_next_value_(name, start, count, last_values):
        return name


class SetTypes(CharEnum):
    STATIC = "static"
    ANIMATED = "animated"
    VIDEO = "video"
    EMOJI = "custom_emoji"


class User(Model):
    user_id = BigIntegerField(unique=True, null=False)
    username = CharField(max_length=32, null=True)
    first_name = CharField(max_length=256, null=False)
    last_name = CharField(max_length=256, null=True)
    language_code = CharField(max_length=3, null=True)
    is_premium = BooleanField(default=False)
    created_at_utc = DateTimeField(default=datetime.utcnow)

    class Meta:
        table_name = 'users'
        database = db


class Set(Model):
    set_type = CharField(choices=SetTypes, null=False)
    user = ForeignKeyField(User, on_delete='CASCADE', backref='sets', null=False)
    name = CharField(max_length=256, null=False)
    title = CharField(max_length=64, null=False)
    created_at_utc = DateTimeField(default=datetime.utcnow)

    class Meta:
        table_name = 'sets'
        database = db
