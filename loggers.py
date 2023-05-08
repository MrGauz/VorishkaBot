import asyncio
import logging

from telegram._bot import BT

from settings import ADMIN_GROUP_ID


class AdminGroupHandler(logging.Handler):
    """
    Custom logging handler to send log messages to the admin group.
    """

    def __init__(self, bot: BT, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.loop = asyncio.get_event_loop()

    def emit(self, record: logging.LogRecord):
        log_entry = f'{record.name} - {record.msg}'
        if record.exc_info:
            exc_type, exc_value, exc_traceback = record.exc_info
            log_entry += f'\n\n{exc_type.__name__}: <code>{str(exc_value)}</code>'

        try:
            task = self.loop.create_task(self.bot.send_message(ADMIN_GROUP_ID, log_entry))
            task.add_done_callback(lambda fut: fut.result())
        except Exception:
            self.handleError(record)
