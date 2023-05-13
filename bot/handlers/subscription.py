import json
import logging
from datetime import datetime
from warnings import filterwarnings

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice
from telegram.constants import ChatAction
from telegram.error import TelegramError
from telegram.ext import ConversationHandler, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.warnings import PTBUserWarning

from bot.handlers.commands import cancel_command
from database.models import ActionTypes, Transaction, User, AnalyticsTypes
from database.utils import store_user, new_analytics_event
from locales import _
from settings import PAYMENT_PROVIDER_TOKEN, PAYMENT_CURRENCY, SUBSCRIPTION_365_PRICE

filterwarnings(action='ignore', message=r'.*CallbackQueryHandler', category=PTBUserWarning)

logger = logging.getLogger(__name__)

SUBSCRIBE = range(1)


async def start_subscription_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Starts the 'subscription' command.

    :param update: Update object containing information about the incoming update.
    :param context: Callback context which contains information about the current state of the bot.
    """
    await update.effective_chat.send_action(ChatAction.TYPING)
    user = store_user(update)
    context.user_data.clear()

    if not user.is_subscribed():
        reply_message = _('subscription.not_active', user.lang_code)
    else:
        reply_message = _('subscription.status', user.lang_code,
                          placeholders={'date': user.subscription_end_date_utc.strftime('%d/%m/%Y')})

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(_('keyboards.subscribe', user.lang_code), callback_data=ActionTypes.SUBSCRIBE_365)],
        [InlineKeyboardButton(_('keyboards.cancel', user.lang_code), callback_data=ActionTypes.CANCEL)]
    ])

    await update.message.reply_text(reply_message, reply_markup=keyboard)
    new_analytics_event(AnalyticsTypes.SUBSCRIBE_COMMAND, update, user)

    return SUBSCRIBE


async def generate_invoice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Generates an invoice for subscription.

    :param update: Update object containing information about the incoming update.
    :param context: Callback context which contains information about the current state of the bot.
    """
    await update.effective_chat.send_action(ChatAction.TYPING)
    user = store_user(update)
    query = update.callback_query

    if query.data != ActionTypes.SUBSCRIBE_365:
        return await cancel_command(update, context)

    try:
        await update.effective_message.reply_invoice(
            title=_('subscription.invoice_title', user.lang_code),
            description=_('subscription.invoice_description', user.lang_code),
            payload=ActionTypes.SUBSCRIBE_365.value,
            provider_token=PAYMENT_PROVIDER_TOKEN,
            currency=PAYMENT_CURRENCY,
            prices=[
                LabeledPrice(label=_('subscription.invoice_title', user.lang_code), amount=SUBSCRIPTION_365_PRICE),
            ],
            photo_url='https://gauz.net/zhopa.jpg',  # TODO: replace
            photo_width=800,  # TODO: replace
            photo_height=800,  # TODO: replace
        )
        new_analytics_event(AnalyticsTypes.INVOICE_GENERATED, update, user)
    except TelegramError as e:
        logger.critical(f'Failed to generate invoice: {e}\nupdate={json.dumps(update.to_dict())}', exc_info=e)
        await update.effective_message.reply_text(_('errors.invoice_generation', user.lang_code))

    return ConversationHandler.END


async def pre_checkout_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the pre-checkout query.

    :param update: Update object containing information about the incoming update.
    :param context: Callback context which contains information about the current state of the bot.
    """
    user = store_user(update)
    if update.pre_checkout_query.invoice_payload != ActionTypes.SUBSCRIBE_365:
        return await update.pre_checkout_query.answer(ok=False,
                                                      error_message=_('subscription.deny_precheckout', user.lang_code))

    try:
        await update.pre_checkout_query.answer(ok=True)
    except TelegramError as e:
        logger.critical(f'Failed to approve pre_checkout_query: {e}\nupdate={json.dumps(update.to_dict())}', exc_info=e)
        await update.effective_message.reply_text(_('errors.pre_checkout_query_failed', user.lang_code))


async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles successful payment.

    :param update: Update object containing information about the incoming update.
    :param context: Callback context which contains information about the current state of the bot.
    """
    await update.effective_chat.send_action(ChatAction.TYPING)
    user = store_user(update)
    payment_info = update.effective_message.successful_payment

    Transaction.create(user=user, invoice_type=payment_info.invoice_payload,
                       currency=payment_info.currency, total_amount=payment_info.total_amount,
                       telegram_payment_charge_id=payment_info.telegram_payment_charge_id,
                       provider_payment_charge_id=payment_info.provider_payment_charge_id)

    end_date = user.subscription_end_date_utc or datetime.utcnow()
    user.subscription_end_date_utc = end_date.replace(year=end_date.year + 1)
    user.save()

    await update.effective_message.reply_text(
        _('subscription.payment_success', user.lang_code,
          placeholders={'date': user.subscription_end_date_utc.strftime('%d/%m/%Y')}))
    new_analytics_event(AnalyticsTypes.USER_SUBSCRIBED, update, user)


async def subscription_reminder(context: ContextTypes.DEFAULT_TYPE):
    """
    Sends a subscription expiration reminder to users.

    :param context: Callback context which contains information about the current state of the bot.
    """
    users = User.select().where(User.subscription_end_date_utc is not None)
    for user in list(users):
        end_date = user.subscription_end_date_utc
        days_left = (end_date - datetime.utcnow()).days
        if user.is_subscribed() and days_left < 3:
            await context.bot.send_chat_action(chat_id=user.user_id, action=ChatAction.TYPING)
            await context.bot.send_message(chat_id=user.user_id,
                                           text=_('subscription.renewal_reminder', user.lang_code,
                                                  placeholders={'days_left': days_left}))


subscription_command = ConversationHandler(
    entry_points=[CommandHandler('subscription', start_subscription_command)],
    states={
        SUBSCRIBE: [CallbackQueryHandler(generate_invoice)]
    },
    fallbacks=[CommandHandler('cancel', cancel_command)],
    per_user=True
)
