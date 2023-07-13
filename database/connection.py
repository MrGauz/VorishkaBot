import logging
import sys

from peewee import MySQLDatabase, OperationalError

from settings import DB_NAME, DB_USER, DB_PORT, DB_HOST, DB_PASS

logger = logging.getLogger(__name__)

db = MySQLDatabase(DB_NAME,
                   user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT,
                   charset='utf8mb4')

try:
    db.connect()
    db.close()
except OperationalError as e:
    logger.error(f'Could not establish a database connection: {e}')
    sys.exit(1)
