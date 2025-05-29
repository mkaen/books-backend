import requests
from logger.logger_config import logger


def validate_image_url(url):
    """Check image url and return True if it exists and image file is correct and undamaged."""
    try:
        response = requests.get(url)
        if response.status_code == 200 and 'image' in response.headers['Content-Type']:
            logger.info(f"Url {url} validation was successful")
            return True
        else:
            logger.info(f"Url {url} validation failure")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error checking URL: {e}")
        return False
