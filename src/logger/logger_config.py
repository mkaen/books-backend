import logging
import os

from src.logger.utils import formatter, console_formatter
from src.constants import LOGGER_LOCATION

LOGGER_NAME = "books-backend"


logger = logging.getLogger(LOGGER_NAME)
logger.setLevel(logging.INFO)


def configure_logger():
    os.makedirs(os.path.dirname(LOGGER_LOCATION), exist_ok=True)

    file_handler = logging.FileHandler(LOGGER_LOCATION, mode="a")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
