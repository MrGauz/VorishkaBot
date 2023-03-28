from datetime import datetime
from enum import Enum

from peewee import Model, BigIntegerField, CharField, BooleanField, DateTimeField, ForeignKeyField

from database.connection import db


class SetTypes(Enum):
    STATIC = 1
    ANIMATED = 2
    VIDEO = 3
    EMOJI = 4


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


class SetType(Model):
    name = CharField(max_length=20, unique=True, null=False)

    class Meta:
        table_name = 'set_types'
        database = db


class Set(Model):
    set_type = ForeignKeyField(SetType, on_delete='CASCADE', backref='sets', null=False)
    user = ForeignKeyField(User, on_delete='CASCADE', backref='sets', null=False)
    name = CharField(max_length=256, null=False)
    title = CharField(max_length=64, null=False)
    created_at_utc = DateTimeField(default=datetime.utcnow)

    class Meta:
        table_name = 'sets'
        database = db
