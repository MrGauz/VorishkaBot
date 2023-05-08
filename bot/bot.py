import logging

from telegram import BotCommand
from telegram._bot import BT
from telegram.constants import BotDescriptionLimit

from settings import ALL_LANGUAGES
from locales import _

logger = logging.getLogger(__name__)


async def setup_bot(bot: BT):
    """
    Set bot commands, description and about.

    :param bot: Bot object.
    """
    await set_bot_commands(bot)
    await set_bot_description(bot)
    await set_bot_about(bot)


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
        desc = _('bot.description', lang_code)[:BotDescriptionLimit.MAX_DESCRIPTION_LENGTH]
        await bot.set_my_description(desc, language_code=lang_code)


async def set_bot_about(bot: BT):
    """
    Set bot short description for every language.

    :param bot: Bot object.
    """
    logger.info('Setting bot about...')
    b = await bot.get_me()
    for lang_code in list(ALL_LANGUAGES.keys()):
        about = _('bot.about', lang_code, placeholders={'bot_username': b.username})[
                :BotDescriptionLimit.MAX_SHORT_DESCRIPTION_LENGTH]
        await bot.set_my_short_description(about, language_code=lang_code)
