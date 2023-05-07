from datetime import datetime
from enum import Enum

from peewee import Model, BigIntegerField, CharField, BooleanField, DateTimeField, ForeignKeyField, IntegerField

from database.connection import db


class CharEnum(str, Enum):
    """A custom Enum subclass that inherits from both str and Enum,
    so that the enum members are automatically converted to string."""

    def _generate_next_value_(name, start, count, last_values):
        return name


class ActionTypes(CharEnum):
    """
    Enum representing various action types that can be performed in the bot.
    """
    RENAME_SET = 'rename_set'
    DELETE_SET = 'delete_set'
    CHANGE_EMOJI = 'change_emoji'
    MOVE_STICKER = 'move_sticker'
    NEW_SET = 'new_set'
    DELETE_STICKER = 'delete_sticker'
    SUBSCRIBE_365 = 'subscribe_365'
    CANCEL = 'cancel'
    BROADCAST = 'broadcast'


class SetTypes(CharEnum):
    """
    Enum representing various sticker set types.
    """
    VIDEO = 'video'
    EMOJI = 'custom_emoji'


class User(Model):
    """
    Model representing a Telegram user.
    """
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
        """
        Checks if user has an active subscription.
        :return: True if user has an active subscription, False otherwise.
        """
        return self.subscription_end_date_utc is not None and self.subscription_end_date_utc > datetime.utcnow()


class Set(Model):
    """
    Model representing a sticker set.
    """
    set_type = CharField(choices=SetTypes, null=False)
    user = ForeignKeyField(User, on_delete='CASCADE', backref='sets', null=False)
    name = CharField(max_length=256, null=False)
    title = CharField(max_length=64, null=False)
    created_at_utc = DateTimeField(default=datetime.utcnow)

    class Meta:
        table_name = 'sets'
        database = db


class Transaction(Model):
    """
    Model representing a payment transaction.
    """
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


class Voucher(Model):
    """
    Model representing a voucher.
    """
    codeword = CharField(max_length=100, unique=True, null=False)
    additional_days = IntegerField(null=False)
    created_at_utc = DateTimeField(default=datetime.utcnow)
    used_at_utc = DateTimeField(null=True, default=None)
    used_by = ForeignKeyField(User, on_delete='CASCADE', backref='vouchers', null=True)

    class Meta:
        table_name = 'vouchers'
        database = db
