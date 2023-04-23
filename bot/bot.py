from telegram import BotCommand
from telegram._bot import BT

from settings import ALL_LANGUAGES
from locales import _


async def set_bot_commands(bot: BT):
    for lang_code in list(ALL_LANGUAGES.keys()):
        await bot.set_my_commands([
            BotCommand(command='my_sets', description=_('bot.my_sets_desc', lang_code)),
            BotCommand(command='translate', description=_('bot.translate_desc', lang_code)),
            BotCommand(command='help', description=_('bot.help_decs', lang_code))
        ], language_code=lang_code)


async def set_bot_description(bot: BT):
    for lang_code in list(ALL_LANGUAGES.keys()):
        await bot.set_my_description(_('bot.description', lang_code), language_code=lang_code)
        await bot.set_my_short_description('А так?', language_code=lang_code)


async def set_bot_about(bot: BT):
    for lang_code in list(ALL_LANGUAGES.keys()):
        await bot.set_my_short_description(_('bot.about', lang_code), language_code=lang_code)
