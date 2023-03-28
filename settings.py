import logging
import os

from dotenv import load_dotenv

load_dotenv()

DEBUG = os.getenv('DEBUG').lower() == 'true'

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Database
if DEBUG:
    DB_NAME = os.getenv('SQLITE_PATH') or 'db.sqlite'
else:
    DB_NAME = os.getenv('MYSQL_NAME', 'vorishka_bot')
DB_HOST = os.getenv('MYSQL_HOST', 'localhost')
DB_PORT = int(os.getenv('MYSQL_PORT', 3306))
DB_USER = os.getenv('MYSQL_USER', 'vorishka_bot')
DB_PASS = os.getenv('MYSQL_PASS', '')

# Logging
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
LOG_LEVEL = logging.INFO
