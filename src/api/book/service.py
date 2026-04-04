from sqlalchemy import text
from flask import jsonify

from src.schemas.schemas import BookSchema
from src.db.helper import send_query_to_database

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
