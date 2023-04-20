import logging
import os

from dotenv import load_dotenv

load_dotenv()

DEBUG = os.getenv('DEBUG').lower() == 'true'

# Telegram
TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
ADMIN_ID = os.environ['ADMIN_ID']

# Payments
PAYMENT_PROVIDER_TOKEN = os.environ['PAYMENT_PROVIDER_TOKEN']
# https://core.telegram.org/bots/payments#supported-currencies
PAYMENT_CURRENCY = os.getenv('PAYMENT_CURRENCY') or 'UAH'

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
ALL_LANGUAGES = {'en': '\U0001f1ec\U0001f1e7', 'ru': '\U0001f1f7\U0001f1fa'}
DEFAULT_LANG = os.getenv('DEFAULT_LANG') or 'en'
if not os.path.isfile(f'locales/translations/{DEFAULT_LANG}.json'):
    raise ValueError(
        f'locales/translations/{DEFAULT_LANG}.json not found - the bot can\'t run without the DEFAULT_LANG translation')

# Stickers
DEFAULT_VIDEO_SET_NAME = 'stickers_%s_by_%s'
DEFAULT_ANIMATED_SET_NAME = 'animated_stickers_%s_by_%s'
DEFAULT_EMOJI_SET_NAME = 'emoji_%s_by_%s'
DEFAULT_NEW_STICKER_EMOJI = u'\U0001F602'
ANIMATED_SET_EMOJI = u'\U0001F304'
EMOJI_SET_EMOJI = u'\U0001F47D'
EMOJI_ONLY_REGEX = "[^\U0001F000-\U0001F999]+"
MAX_FILE_SIZE = 20971520  # 20 MB
