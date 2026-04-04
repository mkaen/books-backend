from sqlalchemy import text
from flask_login import current_user
from flask import jsonify
from datetime import datetime, timedelta

from src.db.dao import db
from src.schemas.schemas import BookSchema
from src.db.helper import send_query_to_database
from src.models.models import Book, User
from src.logger.logger_config import logger
from src.utilities.service import validate_image_url

from src.constants import DEFAULT_TIMEZONE

book_schema = BookSchema()


def handle_book_activity(book_id):
    book = db.get_or_404(Book, book_id)
    if not _is_book_owner(book):
        return jsonify({"msg": f"Current user id: {current_user.id} cannot change book id {book.id} activity toggle."
                               f"Book owner id: {book.owner_id}"}), 401
    if not book.lent_out:
        # query = text("""UPDATE books SET active = :activation, updated_at = timezone(:tz, NOW())
        # WHERE id = :book_id""")
        # send_query_to_database(query, {'activation': not book.active, 'book_id': book_id, 'tz': DEFAULT_TIMEZONE})
        book.active = not book.active
        db.session.commit()
        logger.info(f"(Book id: {book.id}) activity set to {book.active}")
        return jsonify({"message": f"Book availability: {book.active}",
                        "data": book.active}), 200
    return jsonify(success=False, error="Unable to switch book activity toggle."), 400


def _is_book_owner(book):
    return book.owner_id == current_user.id


def handle_return_book(book_id):
    book = db.get_or_404(Book, book_id)
    if current_user.id not in (book.owner_id, book.lender_id):
        return jsonify({"message": f"Unauthorized to return book id {book_id}"}), 401
    # query = text("""UPDATE books
    # SET
    # return_date = NULL,
    # reserved = FALSE,
    # lender_id = NULL,
    # lent_out = FALSE,
    # updated_at = timezone(:tz, NOW())
    # WHERE id = :id
    # """)
    # send_query_to_database(query, {'id': book_id, 'tz': DEFAULT_TIMEZONE})
    book.return_date = None
    book.reserved = False
    book.lender_id = None
    book.lent_out = False
    db.session.commit()
    logger.info(f"User id: {current_user.id} returned book {book.title} (id: {book.id}) successfully to it's owner")
    return jsonify({"message": f"Book id {book_id} returned successfully"}), 200


def handle_reserve_book(book_id):
    book = db.get_or_404(Book, book_id)
    if book.owner_id == current_user.id:
        return jsonify({"message": "Book owner cannot reserve own book"}), 400
    if book.reserved:
        logger.info(f"Failed to reserve book {book_id}")
        return jsonify({"message": f"Failed to reserve book {book_id}"}), 400

    # query = text("""UPDATE books SET
    #      reserved = TRUE,
    #      lender_id = :lender_id,
    #      updated_at = timezone(:tz, NOW())
    #      WHERE id = :book_id
    #      """)
    #
    # params = {
    #     "book_id": book.id,
    #     "lender_id": current_user.id,
    #     "tz": DEFAULT_TIMEZONE
    # }
    # send_query_to_database(query, params)
    book.reserved = True
    book.lender_id = current_user.id
    db.session.commit()

    logger.info(f"User id: {current_user.id} reserved book id: {book.id} successfully")
    return jsonify({"message": f"Book id: {book_id} reserved successfully to lender id: {current_user.id}"}), 200


def handle_cancel_reservation(book_id):
    book = db.get_or_404(Book, book_id)
    message = f"Failed to cancel book id {book_id} reservation"
    if not book.reserved:
        message = f"Book reservation cancellation FAILED, Book id: {book_id}. Book is not reserved"
        logger.error(message)
        return jsonify({"msg": message}), 400
    if book.reserved and _is_valid_person_to_cancel_book_reservation(book):
        # query = text("""UPDATE books SET
        # reserved=FALSE,
        # lender_id=NULL,
        # updated_at = timezone(:tz, NOW())
        # WHERE
        # id=:id
        # """)
        # send_query_to_database(query, {'id': book_id, 'tz': DEFAULT_TIMEZONE})
        book.reserved = False
        book.book_lender = None
        db.session.commit()
        message = f"Successfully cancelled book id {book_id} reservation"
        logger.info(message)
        return jsonify({"message": message}), 200
    logger.error(message)
    return jsonify({"message": message}), 401


def _is_valid_person_to_cancel_book_reservation(book):
    return book.owner_id == current_user.id or book.book_lender.id == current_user.id


def handle_receive_book(book_id):
    book = db.get_or_404(Book, book_id)
    if book.lent_out:
        message = f"Book id {book_id} is already lent out"
        logger.info(message)
        return jsonify({"message": message}), 400
    if current_user in (book.book_owner, book.book_lender):
        current_date = datetime.now().date()
        book_owner = User.query.get(book.owner_id)
        return_date = current_date + timedelta(days=book_owner.duration)
        # query = text("""UPDATE books SET
        #  return_date = :return_date,
        #  lent_out = TRUE,
        #  updated_at = timezone(:tz, NOW())
        #  WHERE id = :id
        # """)
        # send_query_to_database(query, {'return_date': return_date, 'id': book_id, 'tz': DEFAULT_TIMEZONE})
        book.return_date = return_date
        book.lent_out = True
        db.session.commit()
        message = f"Book id {book_id} received successfully"
        logger.info(message)
        return jsonify({"message": message, "returnDate": return_date.strftime("%d-%m-%Y")}), 200
    message = f"Unauthorized to receive book id {book_id}"
    logger.info(message)
    return jsonify({"message": message}), 401


def handle_remove_book(book_id):
    book = db.get_or_404(Book, book_id)
    msg = f"Book id {book_id} removed from database"
    if current_user.id != book.owner_id:
        msg = "Book cannot be removed by non book owner"
        logger.info(msg)
        return jsonify({"message": msg}), 401
    if book.lent_out or book.reserved:
        msg = "Cannot remove book while it's reserved or lent out"
        logger.info(msg)
        return jsonify({"message": msg}), 400
    # query = text("""DELETE FROM books WHERE id = :id""")
    # send_query_to_database(query, {'id': book_id})
    db.session.delete(book)
    db.session.commit()
    logger.info(msg)
    return jsonify({"message": msg}), 200


def handle_add_new_book(data):
    title = data.get('title').title()
    author = data.get('author').title()
    image_url = data.get('image_url')
    description = data.get('description')
    if len(author) < 4:
        return jsonify({"msg": f"Author value: {author} is too short."}), 400

    if not validate_image_url(image_url):
        return jsonify({"msg": f"Book {title} image URL is invalid"}), 409

    # existing_book_query = text("""SELECT * FROM books
    # WHERE
    # title = :title
    # AND
    # author = :author
    # """)
    # existing_book = send_query_to_database(existing_book_query, {'title': title, 'author': author})

    if book_exists(title, author):
        msg = f"Book {title} already exists in database"
        logger.info(msg)
        return jsonify({"msg": msg}), 409

    # add_book_query = text("""INSERT INTO books
    # (title,
    # author,
    # image_url,
    # return_date,
    # reserved,
    # lent_out,
    # owner_id,
    # active,
    # description)
    # VALUES (
    # :title,
    # :author,
    # :image_url,
    # NULL,
    # FALSE,
    # FALSE,
    # :owner_id,
    # TRUE,
    # :description
    # )
    # RETURNING id
    # """)
    #
    # new_book_id = send_query_to_database(add_book_query, {
    #     'title': title,
    #     'author': author,
    #     'image_url': image_url,
    #     'owner_id': current_user.id,
    #     'description': description
    # }
    #                                      )
    new_book = Book(
        title=title,
        author=author,
        image_url=image_url,
        description=description,
        owner_id=current_user.id
    )
    db.session.add(new_book)
    db.session.commit()
    # book = Book.query.get(new_book_id[0])
    msg = f"New book: {title} added successfully."
    logger.info(msg)
    return jsonify({"message": msg, "data": book_schema.dump(new_book)}), 201


def book_exists(title, author):
    return Book.query.filter_by(
        title=title,
        author=author
    ).first() is not None


def validate_new_book_data(data):
    author = data.get('author')
    if not data.get('title'):
        return jsonify({"msg": "Book has no title"}), 400

    if len(author) < 4:
        return jsonify({"msg": f"Author value: {author} is too short."}), 400

    if not validate_image_url(data.get('image_url')):
        return jsonify({"msg": f"Book {data.get('title')} image URL is invalid"}), 409

