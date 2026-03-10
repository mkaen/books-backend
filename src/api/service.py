from sqlalchemy import text
from flask import jsonify

from src.logger.logger_config import logger
from src.schemas.schemas import BookSchema
from src.db.helper import send_query_to_database
from src.db.dao import db
from src.models.models import User

from src.constants import MIN_LEND_DURATION, MAX_LEND_DURATION, DEFAULT_TIMEZONE

books_schema = BookSchema(many=True)


def fetch_all_books():
    query = text("""
    SELECT * FROM books ORDER BY created_at DESC
    """)
    response = send_query_to_database(query)
    books = books_schema.dump(response)
    return jsonify(books)


def fetch_user_books(user_id):
    query = text("""
    SELECT * FROM books WHERE owner_id = :p
    ORDER BY created_at DESC
    """)

    response = send_query_to_database(query, {'p': user_id})
    books = books_schema.dump(response)
    if not response:
        return jsonify([]), 200
    # books = db.session.execute(db.select(Book).where(Book.owner_id == user_id)).scalars()
    return jsonify(books), 200


def fetch_user_reserved_books(user_id):
    query = text("""
    SELECT * FROM books
    WHERE
    reserved=TRUE
    AND
    lender_id=:p
    """)

    response = send_query_to_database(query, {'p': user_id})
    books = books_schema.dump(response)
    return jsonify(books), 200


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
    query = text("""
        UPDATE users SET duration = :d, updated_at = timezone(:tz, NOW())
        WHERE id = :id
        """)

    send_query_to_database(query, {'d': int(duration), 'id': user_id, 'tz': DEFAULT_TIMEZONE})
    # user.duration = duration
    # db.session.commit()
    logger.info(f"User id: {user_id} changed successfully his lending"
                f" period from {previous_duration} days to {duration} days")
    return jsonify({"message": f"Successfully changed user id: {user_id} book lending duration to {duration}"}), 200
