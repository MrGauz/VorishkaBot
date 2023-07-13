import logging
import os

from dotenv import load_dotenv

load_dotenv()

DEBUG = os.getenv('DEBUG').lower() == 'true'

# Telegram
TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
ADMIN_GROUP_ID = int(os.environ['ADMIN_GROUP_ID'])
CONTEXT_DATA_PATH = 'context_data'
CONCURRENT_THREADS = int(os.getenv('CONCURRENT_THREADS') or 3)

# Payments
PAYMENT_PROVIDER_TOKEN = os.environ['PAYMENT_PROVIDER_TOKEN']
# https://core.telegram.org/bots/payments#supported-currencies
PAYMENT_CURRENCY = os.getenv('PAYMENT_CURRENCY') or 'UAH'
SUBSCRIPTION_365_PRICE = int(os.environ['SUBSCRIPTION_365_PRICE'])

# Database
DB_NAME = 'vorishka_bot'
DB_HOST = os.getenv('MYSQL_HOST') or 'mysql'
DB_PORT = 3306
DB_USER = 'vorishka_bot'
DB_PASS = os.getenv('MYSQL_PASSWORD') or 'vorishka_bot'

# Logging
LOGS_PATH = os.getenv('LOG_PATH') or 'logs'
if not os.path.isdir(LOGS_PATH):
    os.mkdir(LOGS_PATH)
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
LOG_LEVEL = logging.INFO
LOGGING_CONFIG = {
    'version': 1,
    'formatters': {
        'default': {'format': LOG_FORMAT},
    },
    'handlers': {
        'console': {'class': 'logging.StreamHandler', 'formatter': 'default', 'level': LOG_LEVEL},
        'file': {'class': 'logging.handlers.RotatingFileHandler', 'formatter': 'default',
                 'filename': f'{LOGS_PATH}/bot.log', 'maxBytes': 1048576, 'level': LOG_LEVEL},
    },
    'loggers': {
        '': {'handlers': ['console', 'file'], 'level': LOG_LEVEL},
    },
}

# Translations
ALL_LANGUAGES = {'en': '\U0001F1EC\U0001F1E7', 'ru': '\U0001F1F7\U0001F1FA', 'uk': '\U0001F1FA\U0001F1E6'}
DEFAULT_LANG = os.getenv('DEFAULT_LANG') or 'en'
if not os.path.isfile(f'locales/translations/{DEFAULT_LANG}.json'):
    raise ValueError(
        f'locales/translations/{DEFAULT_LANG}.json not found - the bot can\'t run without the DEFAULT_LANG translation')

# Stickers
DEFAULT_VIDEO_SET_NAME = 'stickers_%s_by_%s'
DEFAULT_EMOJI_SET_NAME = 'emoji_%s_by_%s'
DEFAULT_STICKER_EMOJI = u'\U0001F602'
VIDEO_SET_EMOJI = u'\U0001F304'
EMOJI_SET_EMOJI = u'\U0001F47D'
MAX_FILE_SIZE = 20971520  # 20 MB

# TGS to WEBM converter
TGS_CONVERTER_PATH = os.getenv('TGS_CONVERTER_PATH') or '/converter/TgsConverter.dll'
if not os.path.isfile(TGS_CONVERTER_PATH):
    raise OSError(f'TGS converter not found at {TGS_CONVERTER_PATH}')
