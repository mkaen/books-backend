import logging
import os
from dotenv import load_dotenv

load_dotenv()
LOGGER_LOCATION = os.environ.get('LOGGER_LOCATION')

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger_handler = logging.FileHandler(LOGGER_LOCATION)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger_handler.setFormatter(formatter)
logger.addHandler(logger_handler)