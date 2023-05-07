from telegram.ext.filters import MessageFilter

from database.models import Voucher, User, Set
from settings import ADMIN_GROUP_ID


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


class AdminChatFilter(MessageFilter):
    """
    Custom filter class to check if a message is from an admin chat.
    """

    def filter(self, message):
        """
        Check if a message is from an admin chat.

        :param message: Message object to be checked.
        :return: True if the message is from an admin chat, False otherwise.
        """
        return message.chat_id == ADMIN_GROUP_ID


admin_group_filter = AdminChatFilter()
