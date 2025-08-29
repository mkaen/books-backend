import logging
import os
from dotenv import load_dotenv

from logger.utils import get_current_time

load_dotenv()
LOGGER_LOCATION = os.environ.get("LOGGER_LOCATION", "logs/app.log")

logger = logging.getLogger("books-backend")
logger.setLevel(logging.INFO)

formatter = f"[{get_current_time()}] - %(name)s - %(levelname)s - %(message)s"

if not logger.handlers:
    file_handler = logging.FileHandler(LOGGER_LOCATION)
    file_handler.setFormatter(logging.Formatter(formatter))

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        f"[{get_current_time()}] - %(levelname)s - %(message)s"
    ))

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
