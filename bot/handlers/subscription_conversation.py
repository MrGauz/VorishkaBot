import logging
from datetime import datetime
from warnings import filterwarnings

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice
from telegram.ext import ConversationHandler, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.warnings import PTBUserWarning

from bot.handlers.commands import cancel_command
from database.models import ActionTypes, Transaction
from database.utils import store_user
from locales import _
from settings import PAYMENT_PROVIDER_TOKEN, PAYMENT_CURRENCY, SUBSCRIPTION_365_PRICE

filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)

logger = logging.getLogger(__name__)

SUBSCRIBE = range(1)


async def start_subscription_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = store_user(update)
    context.user_data.clear()

    if not user.is_subscribed():
        reply_message = _('subscription.subscription_not_active', user.lang_code)
    else:
        reply_message = _('subscription.subscription_status', user.lang_code,
                          placeholders={'date': user.subscription_end_date_utc.strftime("%d/%m/%Y")})

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(_('buttons.subscribe', user.lang_code), callback_data=ActionTypes.SUBSCRIBE_365)],
        [InlineKeyboardButton(_('buttons.cancel', user.lang_code), callback_data=ActionTypes.CANCEL)]
    ])

    await update.message.reply_text(reply_message, reply_markup=keyboard)

    return SUBSCRIBE


async def generate_invoice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = store_user(update)
    query = update.callback_query

    if query.data != ActionTypes.SUBSCRIBE_365:
        return await cancel_command(update, context)

    await update.effective_message.reply_invoice(
        title=_("subscription.invoice_title", user.lang_code),
        description=_("subscription.invoice_description", user.lang_code),
        payload=ActionTypes.SUBSCRIBE_365.value,
        provider_token=PAYMENT_PROVIDER_TOKEN,
        currency=PAYMENT_CURRENCY,
        prices=[
            LabeledPrice(label=_("subscription.invoice_title", user.lang_code), amount=SUBSCRIPTION_365_PRICE),
        ],
        photo_url='https://gauz.net/zhopa.jpg',  # TODO: replace
        photo_width=800,  # TODO: replace
        photo_height=800,  # TODO: replace
    )

    return ConversationHandler.END


async def pre_checkout_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = store_user(update)
    if update.pre_checkout_query.invoice_payload != ActionTypes.SUBSCRIBE_365:
        return await update.pre_checkout_query.answer(ok=False,
                                                      error_message=_('subscription.deny_precheckout', user.lang_code))

    await update.pre_checkout_query.answer(ok=True)


async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = store_user(update)
    payment_info = update.effective_message.successful_payment

    transaction = Transaction()
    transaction.user = user
    transaction.invoice_type = payment_info.invoice_payload
    transaction.currency = payment_info.currency
    transaction.total_amount = payment_info.total_amount
    transaction.telegram_payment_charge_id = payment_info.telegram_payment_charge_id
    transaction.provider_payment_charge_id = payment_info.provider_payment_charge_id
    transaction.save()

    end_date = user.subscription_end_date_utc or datetime.utcnow()
    user.subscription_end_date_utc = end_date.replace(year=end_date.year + 1)
    user.save()

    await update.effective_message.reply_text(
        _('subscription.payment_success', user.lang_code,
          placeholders={'date': user.subscription_end_date_utc.strftime("%d/%m/%Y")}))


subscription_command = ConversationHandler(
    entry_points=[CommandHandler('subscription', start_subscription_command)],
    states={
        SUBSCRIBE: [CallbackQueryHandler(generate_invoice)]
    },
    fallbacks=[CommandHandler('cancel', cancel_command)],
    per_user=True
)
