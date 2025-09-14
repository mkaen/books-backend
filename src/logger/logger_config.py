import logging
import os

from dotenv import load_dotenv

from logger.utils import formatter, console_formatter

load_dotenv()

LOGGER_LOCATION = os.environ.get("LOGGER_LOCATION", "logs/app.log")
os.makedirs(os.path.dirname(LOGGER_LOCATION), exist_ok=True)

logger = logging.getLogger("books-backend")
logger.setLevel(logging.INFO)


if not logger.handlers:
    file_handler = logging.FileHandler(LOGGER_LOCATION)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_formatter = console_formatter
    console_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
