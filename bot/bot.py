import logging

from telegram import BotCommand
from telegram._bot import BT
from telegram.ext.filters import MessageFilter

from database.models import Set, User, Voucher
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


class PersonalStickerFilter(MessageFilter):
    """
    Custom filter class to check if a message contains a sticker from a user's personal set.
    """

    def filter(self, message):
        """
        Check if a message contains a sticker from a user's personal set.

        :param message: Message object to be checked.
        :return: True if the message contains a personal sticker, False otherwise.
        """
        if not message.sticker:
            return False

        user = User.get_or_none(User.user_id == message.from_user.id)
        user_set = Set.get_or_none(Set.user_id == user, Set.name == message.sticker.set_name)
        if user is None or user_set is None:
            return False

        return True


personal_sticker_filter = PersonalStickerFilter()


class VoucherMessageFilter(MessageFilter):
    """
    Custom filter class to check if a message contains a sticker from a user's personal set.
    """

    def filter(self, message):
        """
        Check if a message contains a sticker from a user's personal set.

        :param message: Message object to be checked.
        :return: True if the message contains a personal sticker, False otherwise.
        """
        if not message.text:
            return False

        voucher = Voucher.get_or_none(Voucher.codeword == message.text)
        if voucher is None:
            return False

        return True


voucher_message_filter = VoucherMessageFilter()
