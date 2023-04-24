from datetime import datetime
from enum import Enum

from peewee import Model, BigIntegerField, CharField, BooleanField, DateTimeField, ForeignKeyField, IntegerField

from database.connection import db


class CharEnum(str, Enum):
    """A custom Enum subclass that inherits from both str and Enum,
    so that the enum members are automatically converted to strings."""

    def _generate_next_value_(name, start, count, last_values):
        return name


class ActionTypes(CharEnum):
    RENAME_SET = "rename_set"
    DELETE_SET = "delete_set"
    CHANGE_EMOJI = "change_emoji"
    DELETE_STICKER = "delete_sticker"
    SUBSCRIBE_365 = "subscribe_365"
    CANCEL = "cancel"


class SetTypes(CharEnum):
    # TODO: custom emoji can be of each of the sticker types
    ANIMATED = "animated"
    VIDEO = "video"
    EMOJI = "custom_emoji"


class User(Model):
    user_id = BigIntegerField(unique=True, null=False)
    username = CharField(max_length=32, null=True)
    first_name = CharField(max_length=256, null=False)
    last_name = CharField(max_length=256, null=True)
    lang_code = CharField(max_length=3, null=True)
    is_premium = BooleanField(default=False)
    subscription_end_date_utc = DateTimeField(null=True, default=None)
    created_at_utc = DateTimeField(default=datetime.utcnow)

    class Meta:
        table_name = 'users'
        database = db

    def is_subscribed(self) -> bool:
        return self.subscription_end_date_utc is not None and self.subscription_end_date_utc > datetime.utcnow()


class Set(Model):
    set_type = CharField(choices=SetTypes, null=False)
    user = ForeignKeyField(User, on_delete='CASCADE', backref='sets', null=False)
    name = CharField(max_length=256, null=False)
    title = CharField(max_length=64, null=False)
    created_at_utc = DateTimeField(default=datetime.utcnow)

    class Meta:
        table_name = 'sets'
        database = db


class Transaction(Model):
    user = ForeignKeyField(User, on_delete='CASCADE', backref='transactions', null=False)
    invoice_type = CharField(max_length=100, null=False)
    currency = CharField(max_length=5, null=False)
    total_amount = IntegerField(null=False)
    telegram_payment_charge_id = CharField(max_length=100, null=False)
    provider_payment_charge_id = CharField(max_length=100, null=False)
    created_at_utc = DateTimeField(default=datetime.utcnow)

    class Meta:
        table_name = 'transactions'
        database = db
