
from sqlalchemy import text
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

from schemas.schemas import AddNewBookSchema
from src.api.book.utils import handle_book_activity, handle_return_book, handle_reserve_book, handle_cancel_reservation, \
    handle_receive_book, handle_remove_book, handle_add_new_book
from src.db.dao import db
from src.models.models import Book
from src.logger.logger_config import logger
from src.utilities.service import validate_image_url
from src.db.helper import send_query_to_database
from src.api.book.service import fetch_all_books, fetch_user_books, fetch_user_reserved_books

book_blueprint = Blueprint('book_api', __name__, url_prefix='/book_api')

add_new_book_schema = AddNewBookSchema()


@book_blueprint.route('/fetch_books', methods=['GET'])
def get_all_the_books():
    return fetch_all_books()


@book_blueprint.route('/user_books/<int:user_id>', methods=['GET'])
@login_required
def get_user_books(user_id):
    if current_user.id != user_id:
        return jsonify({"msg": f"User id: {current_user.id} is not authorized to fetch user id: {user_id} books"}), 401
    return fetch_user_books(user_id)


@book_blueprint.route('/reserved_books/<int:user_id>', methods=['GET'])
@login_required
def get_reserved_books_by_user_id(user_id):
    return fetch_user_reserved_books(user_id)


@book_blueprint.route('/return_book/<int:book_id>', methods=['PATCH'])
@login_required
def return_book(book_id):
    """
    Return book to lending environment.

    Validate book and user. Book can return only book lender or book owner.
    Reset book values.
    :param book_id: Book id
    :return: redirect to home page.
    """
    return handle_return_book(book_id)


@book_blueprint.route('/activity/<int:book_id>', methods=['PATCH'])
@login_required
def book_activity_toggle(book_id):
    """Activate or deactivate your own book for lending out."""
    return handle_book_activity(book_id)


@book_blueprint.route('/reserve_book/<int:book_id>', methods=['PATCH'])
@login_required
def reserve_book(book_id):
    """
    Reserve book if it's not reserved yet.

    :param book_id: Book.id
    :return: redirect to home page
    """
    return handle_reserve_book(book_id)



@book_blueprint.route('/cancel_reservation/<int:book_id>', methods=['PATCH'])
@login_required
def cancel_reservation(book_id):
    """Validate that current user is book lender or book owner and cancel the reservation."""
    return handle_cancel_reservation(book_id)


@book_blueprint.route('/receive_book/<int:book_id>', methods=['PATCH'])
@login_required
def receive_book(book_id):
    """
    Validate book and mark book as handed over to lender.

    :param book_id: Book.id
    :return: redirect to my_reserved_books page
    """
    return handle_receive_book(book_id)


@book_blueprint.route('/remove_book/<int:book_id>', methods=['DELETE'])
@login_required
def remove_book(book_id):
    """Remove a book from the database. Validate that book is not lent out and user is the owner of the book."""
    return handle_remove_book(book_id)


@book_blueprint.route('/add_new_book', methods=['POST'])
@login_required
def add_book():
    """Create and add a new book to the database and lending environment."""
    data = add_new_book_schema.load(request.json)
    return handle_add_new_book(data)
