from telegram import Update
from telegram.ext import ContextTypes

from database.models import Actions
from database.utils import get_user, rename_set
from locales import _


async def text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = await get_user(update)
    text = update.effective_message.text
    action = context.user_data.get('action')

    if action == Actions.RENAME_SET:
        set_name = context.user_data['selected_set']
        result = await context.bot.set_sticker_set_title(set_name, text)
        if result:
            await context.bot.send_message(user.user_id, _('chat.set_renamed_success', user.lang_code,
                                                           {'set_name': set_name, 'new_title': text}))
            await rename_set(set_name, text)
        else:
            await context.bot.send_message(user.user_id,
                                           _('chat.set_renamed_error', user.lang_code, {'new_name': text}))
        context.user_data.clear()
