from warnings import filterwarnings

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, CallbackQueryHandler
from telegram.warnings import PTBUserWarning

from bot.handlers.commands import cancel_command
from bot.message_filters import admin_group_filter
from database.models import Voucher, User, ActionTypes

filterwarnings(action='ignore', message=r'.*CallbackQueryHandler', category=PTBUserWarning)

CONFIRM_BROADCAST = 0


async def add_voucher_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Command handler for adding a voucher. Only available in admin group.
    Takes a codeword and the amount of days to add to the subscription as arguments.
    e.g. /add_voucher you got us 3

    :param update: Update object containing information about the incoming update.
    :param context: Callback context which contains information about the current state of the bot.
    """

    days = context.args[-1]
    codeword = update.effective_message.text[13:-len(days) - 1].strip()
    Voucher.create(codeword=codeword, additional_days=days)

    await update.effective_message.reply_text(f"Voucher saved")


async def list_vouchers_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Command handler for listing all unused vouchers. Only available in admin group.

    :param update: Update object containing information about the incoming update.
    :param context: Callback context which contains information about the current state of the bot.
    """

    vouchers = Voucher.select().where(Voucher.used_by.is_null())
    message = 'Unused vouchers:\n\n'
    for voucher in vouchers:
        message += f'"<code>{voucher.codeword}</code>" - {voucher.additional_days} days\n'
    await update.effective_message.reply_text(message)


async def start_broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Command handler for broadcasting a message to all users. Only available in admin group.
    Takes a message as an argument. In this case the message will be sent from bot to all users.
    Alternatively, you can reply to a message with /broadcast to broadcast that message. This forwards the message.

    :param update: Update object containing information about the incoming update.
    :param context: Callback context which contains information about the current state of the bot.
    """

    context.chat_data.clear()
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton('No, stop', callback_data=ActionTypes.CANCEL)],
        [InlineKeyboardButton('Yes, broadcast it', callback_data=ActionTypes.BROADCAST)]])

    if context.args and context.args[0]:
        example_message = await update.effective_message.reply_text(update.effective_message.text_html
                                                                    .replace('/broadcast ', ''))
        context.chat_data['broadcast_message'] = example_message.text_html
        await update.effective_chat.send_message('Do you want to broadcast this message?',
                                                 reply_to_message_id=example_message.message_id,
                                                 reply_markup=keyboard)
        return CONFIRM_BROADCAST
    elif update.effective_message.reply_to_message:
        example_message = await update.effective_message.reply_to_message.forward(chat_id=update.effective_chat.id)
        context.chat_data['broadcast_message_id'] = update.effective_message.reply_to_message.message_id
        context.chat_data['broadcast_message_chat_id'] = update.effective_message.reply_to_message.chat_id
        await update.effective_chat.send_message('Do you want to broadcast this message?',
                                                 reply_to_message_id=example_message.message_id,
                                                 reply_markup=keyboard)
        return CONFIRM_BROADCAST
    else:
        await update.effective_message.reply_text('Please reply to a message or provide a message to broadcast')
        context.chat_data.clear()
        return ConversationHandler.END


async def broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Callback handler for broadcasting a message to all users. Only available in admin group.

    :param update: Update object containing information about the incoming update.
    :param context: Callback context which contains information about the current state of the bot.
    """

    await update.callback_query.answer()
    await update.effective_message.delete()

    if update.callback_query.data != ActionTypes.BROADCAST:
        await update.effective_chat.send_message('Broadcast cancelled')
        context.chat_data.clear()
        return ConversationHandler.END

    for user in User.select():
        if 'broadcast_message' in context.chat_data:
            await context.bot.send_message(user.user_id, context.chat_data['broadcast_message'])
        elif 'broadcast_message_id' in context.chat_data and 'broadcast_message_chat_id' in context.chat_data:
            await context.bot.forward_message(user.user_id, context.chat_data['broadcast_message_chat_id'],
                                              context.chat_data['broadcast_message_id'])

    await update.effective_chat.send_message('Broadcast finished')
    context.chat_data.clear()
    return ConversationHandler.END


broadcast_command = ConversationHandler(
    entry_points=[CommandHandler('broadcast', start_broadcast_command, filters=admin_group_filter)],
    states={
        CONFIRM_BROADCAST: [CallbackQueryHandler(broadcast_message)],
    },
    fallbacks=[CommandHandler('cancel', cancel_command)],
    per_user=True
)


async def show_admin_help_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Fallback handler that shows a help message. Only available in admin group.

    :param update: Update object containing information about the incoming update.
    :param context: Callback context which contains information about the current state of the bot.
    """

    message = ('You can use the following commands:\n\n'
               '• /add_voucher &lt;trigger text&gt; &lt;days&gt;\n'
               '• /list_vouchers to list all unused vouchers\n'
               '• /broadcast &lt;message&gt; to send a message to all bot users\n'
               'or reply with /broadcast to a message to forward it \n'
               '• /help to show this message')
    await update.effective_message.reply_text(message)
