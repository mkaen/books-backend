from sqlalchemy import text
from flask import jsonify
from werkzeug.security import generate_password_hash

from src.logger.logger_config import logger
from src.db.helper import send_query_to_database
from src.db.dao import db
from src.models.models import User

from src.constants import MIN_LEND_DURATION, MAX_LEND_DURATION, DEFAULT_TIMEZONE


def handle_duration(user_id, data):
    duration = data.get('duration')
    user = db.get_or_404(User, user_id)
    previous_duration = user.duration

    try:
        duration = int(duration)
    except (ValueError, TypeError):
        return jsonify({"msg": f"Wrong duration format: {duration}"}), 400

    if not duration or not MIN_LEND_DURATION <= duration <= MAX_LEND_DURATION:
        return jsonify({"message": f"Wrong duration format or value: {duration}"}), 400
    # query = text("""
    #     UPDATE users SET duration = :d, updated_at = timezone(:tz, NOW())
    #     WHERE id = :id
    #     """)
    #
    # send_query_to_database(query, {'d': int(duration), 'id': user_id, 'tz': DEFAULT_TIMEZONE})
    user.duration = int(duration)
    db.session.commit()
    logger.info(f"User id: {user_id} changed successfully his lending"
                f" period from {previous_duration} days to {duration} days")
    return jsonify({"message": f"Successfully changed user id: {user_id} book lending duration to {duration}"}), 200


def get_user_data_by_email(email):
    """Fetch user data from database using email."""
    # query = text("""SELECT * FROM users WHERE email = :email""")
    # response = send_query_to_database(query, {'email': email})
    response = User.query.filter_by(email=email).first()
    return response


def save_data_and_fetch_user_id(data):
    # query = text("""INSERT INTO users (first_name, last_name, email, password)
    # VALUES (
    # :first_name,
    # :last_name,
    # :email,
    # :password)
    # RETURNING id
    # """)
    #
    # user_id = send_query_to_database(query, {'first_name': data.get('first_name').title(),
    #                                           'last_name': data.get('last_name').title(),
    #                                           'email': data.get('email').lower(),
    #                                           'password': generate_password_hash(
    #                                               data.get('password'),
    #                                               method='pbkdf2:sha256',
    #                                               salt_length=8
    #                                           )})
    # return user_id[0]
    new_user = User(
        first_name=data.get('first_name').title(),
        last_name=data.get('last_name').title(),
        email=data.get('email').lower(),
        password=generate_password_hash(
            data.get('password'),
            method='pbkdf2:sha256',
            salt_length=8
        )
    )

    db.session.add(new_user)
    db.session.commit()

    return new_user.id

