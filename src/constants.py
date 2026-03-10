import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

if Path('/app').exists():
    ROOT = Path('/app')
else:
    ROOT = Path(__file__).parent.parent


# ENVIRONMENT VARIABLES
DATABASE_URL = os.getenv('DATABASE_URL')
SECRET_KEY = os.getenv("SECRET_KEY")
LOGGER_LOCATION = str(ROOT / "logs" / "book_lending_be.log")

# USER CONSTANTS
DEFAULT_LEND_DURATION = 28
MIN_LEND_DURATION = 7
MAX_LEND_DURATION = 92
DEFAULT_TIMEZONE = "Europe/Tallinn"

# DATABASE
DB_TABLES = {'alembic_version', 'books', 'users'}
