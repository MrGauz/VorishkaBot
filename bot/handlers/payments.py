import json

from telegram import Update, LabeledPrice
from telegram.ext import ContextTypes

from settings import PAYMENT_PROVIDER_TOKEN, PAYMENT_CURRENCY

#application.add_handler(CommandHandler("invoice", invoice_command))
#application.add_handler(PreCheckoutQueryHandler(pre_checkout_query))
#application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))


async def invoice_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_invoice(
        title="Жопа Толстая",
        description="Продается жопа. Не бита, не крашена.",
        payload=str(update.effective_user.id),
        provider_token=PAYMENT_PROVIDER_TOKEN,
        currency=PAYMENT_CURRENCY,
        prices=[
            LabeledPrice(label="Жопа", amount=10000),
            LabeledPrice(label="Нологи", amount=0),
        ],
        photo_url='https://gauz.net/zhopa.jpg',
        photo_width=800,
        photo_height=800,
    )


async def pre_checkout_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.pre_checkout_query.answer(ok=True)


async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    payment_info = update.effective_message.successful_payment
    print(json.dumps(payment_info.to_dict()))
    await update.effective_message.reply_text('Спасибо за покупку жопы за %s %s!' %
                                              (payment_info.total_amount / 100, payment_info.currency))
