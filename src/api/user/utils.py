from flask import jsonify
from werkzeug.security import check_password_hash
from sqlalchemy import text

from src.db.helper import send_query_to_database
from src.logger.logger_config import logger


def compare_passwords(db_value, value):
    """Compare hashed passwords."""
    if not check_password_hash(db_value, value):
        logger.info("Passwords do not match")
        return False
    return True


def validate_user_registration_data(data):
    first_name = data.get('firstName')
    last_name = data.get('lastName')
    email = data.get('email')
    password = data.get('password')
    if not first_name or not last_name or not email or not password:
        msg = "Incoming registration has missing data"
        logger.info(msg)
        return jsonify({"message": msg}), 400


def is_existing_email(email):
    # Try plokki hiljem!

    query = text("""SELECT * FROM users WHERE email = :email""")
    return send_query_to_database(query, {'email': email})
