from telegram import BotCommand
from telegram._bot import BT

from settings import ALL_LANGUAGES
from locales import _


async def set_bot_commands(bot: BT):
    for lang_code in list(ALL_LANGUAGES.keys()):
        await bot.set_my_commands([
            BotCommand(command='rename_set', description=_('bot.rename_set_desc', lang_code)),
            BotCommand(command='delete_set', description=_('bot.rename_set_desc', lang_code)),
            BotCommand(command='translate', description=_('bot.translate_desc', lang_code)),
            BotCommand(command='help', description=_('bot.help_decs', lang_code))
        ], language_code=lang_code)
