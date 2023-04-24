from telegram import BotCommand
from telegram._bot import BT
from telegram.ext.filters import MessageFilter

from database.models import Set, User
from settings import ALL_LANGUAGES
from locales import _


async def set_bot_commands(bot: BT):
    for lang_code in list(ALL_LANGUAGES.keys()):
        await bot.set_my_commands([
            BotCommand(command='my_sets', description=_('bot.my_sets_desc', lang_code)),
            BotCommand(command='subscription', description=_('bot.subscription_desc', lang_code)),
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


class PersonalStickerFilter(MessageFilter):
    def filter(self, message):
        if not message.sticker:
            return False

        user = User.get_or_none(User.user_id == message.from_user.id)
        user_set = Set.get_or_none(Set.user_id == user, Set.name == message.sticker.set_name)
        if user is None or user_set is None:
            return False

        return True


personal_sticker_filter = PersonalStickerFilter()
