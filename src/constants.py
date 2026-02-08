import os
from dotenv import load_dotenv

load_dotenv()


# ENVIRONMENT VARIABLES
DATABASE_URL = os.getenv('DATABASE_URL')
SECRET_KEY = os.getenv("SECRET_KEY")
LOGGER_LOCATION = os.environ.get("LOGGER_LOCATION", "logs/app.log")
LOGGER_TEST_LOCATION = os.environ.get('LOGGER_TEST_LOCATION')

# USER CONSTANTS
DEFAULT_LEND_DURATION = 28
MIN_LEND_DURATION = 7
MAX_LEND_DURATION = 92
TIMEZONE = "Europe/Tallinn"

# DATABASE
DB_TABLES = {'alembic_version', 'books', 'users'}
