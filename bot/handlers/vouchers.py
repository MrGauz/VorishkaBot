from datetime import datetime, timedelta

from telegram import Update
from telegram.ext import ContextTypes

from database.models import Voucher
from database.utils import store_user
from locales import _


async def use_voucher(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler for using a voucher.

    :param update: Update object containing information about the incoming update.
    :param context: Callback context which contains information about the current state of the bot.
    """
    user = store_user(update)
    voucher = Voucher.get_or_none(Voucher.codeword == update.effective_message.text, Voucher.used_by.is_null())

    if voucher is None:
        await update.effective_message.reply_text(_('subscription.voucher_already_used', user.lang_code))
        return

    if user.subscription_end_date_utc is not None:
        user.subscription_end_date_utc = user.subscription_end_date_utc + timedelta(days=voucher.additional_days)
    else:
        user.subscription_end_date_utc = datetime.utcnow() + timedelta(days=voucher.additional_days)
    user.save()

    voucher.used_by = user
    voucher.used_at_utc = datetime.utcnow()
    voucher.save()

    await update.effective_message.reply_text(_('subscription.voucher_activated', user.lang_code,
                                                placeholders={'days': voucher.additional_days}))
