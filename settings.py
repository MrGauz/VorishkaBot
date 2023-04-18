import logging
import os

from dotenv import load_dotenv

load_dotenv()

DEBUG = os.getenv('DEBUG').lower() == 'true'

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')

# Database
if DEBUG:
    DB_NAME = os.getenv('SQLITE_PATH') or 'db.sqlite'
else:
    DB_NAME = os.getenv('MYSQL_NAME') or 'vorishka_bot'
DB_HOST = os.getenv('MYSQL_HOST') or 'localhost'
DB_PORT = int(os.getenv('MYSQL_PORT') or 3306)
DB_USER = os.getenv('MYSQL_USER') or 'vorishka_bot'
DB_PASS = os.getenv('MYSQL_PASS')

# Logging
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
LOG_LEVEL = logging.INFO

# Translations
DEFAULT_LANG = os.getenv('DEFAULT_LANG') or 'en'
if not os.path.isfile(f'locales/translations/{DEFAULT_LANG}.json'):
    raise ValueError(
        f'locales/translations/{DEFAULT_LANG}.json not found - the bot can\'t run without the DEFAULT_LANG translation')

# Stickers
DEFAULT_NEW_STICKER_EMOJI = u'\U0001F602'
DEFAULT_STATIC_SET_NAME = 'stickers_%s_by_%s'
DEFAULT_VIDEO_SET_NAME = 'video_stickers_%s_by_%s'
DEFAULT_ANIMATED_SET_NAME = 'animated_stickers_%s_by_%s'
DEFAULT_EMOJI_SET_NAME = 'emoji_%s_by_%s'
STATIC_SET_EMOJI = u'\U0001F304'
ANIMATED_SET_EMOJI = u'\U0001F3A5'
EMOJI_SET_EMOJI = u'\U0001F47D'
