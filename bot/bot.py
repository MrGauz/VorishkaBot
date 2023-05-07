import logging

from telegram import BotCommand
from telegram._bot import BT

from settings import ALL_LANGUAGES
from locales import _

logger = logging.getLogger(__name__)


async def set_bot_commands(bot: BT):
    """
    Set bot commands for every language.

    :param bot: Bot object.
    """
    logger.info('Setting bot commands...')
    for lang_code in list(ALL_LANGUAGES.keys()):
        await bot.set_my_commands([
            BotCommand(command='my_sets', description=_('bot.my_sets_desc', lang_code)),
            BotCommand(command='subscription', description=_('bot.subscription_desc', lang_code)),
            BotCommand(command='translate', description=_('bot.translate_desc', lang_code)),
            BotCommand(command='help', description=_('bot.help_decs', lang_code))
        ], language_code=lang_code)


async def set_bot_description(bot: BT):
    """
    Set bot description for every language.

    :param bot: Bot object.
    """
    logger.info('Setting bot description...')
    for lang_code in list(ALL_LANGUAGES.keys()):
        await bot.set_my_description(_('bot.description', lang_code), language_code=lang_code)


async def set_bot_about(bot: BT):
    """
    Set bot short description for every language.

    :param bot: Bot object.
    """
    logger.info('Setting bot about...')
    for lang_code in list(ALL_LANGUAGES.keys()):
        await bot.set_my_short_description(_('bot.about', lang_code, placeholders={'bot_username': bot.username}),
                                           language_code=lang_code)
