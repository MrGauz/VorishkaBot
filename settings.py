import logging
import os

from dotenv import load_dotenv

load_dotenv()

DEBUG = os.getenv('DEBUG').lower() == "true"

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Database
if DEBUG:
    DATABASE_ENGINE = 'sqlite:///db.sqlite'
else:
    DATABASE_ENGINE = 'mysql+pymysql://%s:%s@%s/%s' % (
        os.getenv('MYSQL_USER'), os.getenv('MYSQL_PASS'), os.getenv('MYSQL_HOST'), os.getenv('MYSQL_NAME'))

# Logging
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
if DEBUG:
    LOG_LEVEL = logging.DEBUG
else:
    LOG_LEVEL = logging.INFO
