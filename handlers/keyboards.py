from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from database.models import Actions
from database.utils import get_user
from locales import _


async def inline_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = await get_user(update)
    query = update.callback_query
    action = context.user_data['action']

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()

    if action == Actions.RENAME_SET:
        context.user_data['selected_set'] = query.data
        await context.bot.send_message(user.user_id, _('chat.choose_new_set_name', user.lang_code),
                                       parse_mode=ParseMode.HTML)
