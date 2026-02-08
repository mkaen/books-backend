from datetime import datetime, timedelta

from sqlalchemy import text
from flask import request, jsonify
from flask_login import login_required, current_user, logout_user, login_user
from werkzeug.security import generate_password_hash, check_password_hash

from src.db.dao import db
from src.models.models import User, Book
from src.logger.logger_config import logger
from src.auth.routes import user_blueprint, book_blueprint
from src.utilities.service import validate_image_url
from src.db.helper import send_query_to_database
from src.constants import MIN_LEND_DURATION, MAX_LEND_DURATION, DEFAULT_LEND_DURATION


@book_blueprint.route('/fetch_books')
def get_all_the_books():
    query = text("""
    SELECT * FROM books ORDER BY created_at DESC
    """)
    books = send_query_to_database(query)
    return jsonify(books)
    # books = Book.query.all()
    # book_list = [book.to_dict() for book in books]
    # return jsonify(book_list), 200


@book_blueprint.route('/user_books/<int:user_id>')
@login_required
def get_user_books(user_id):
    if current_user.id != user_id:
        return jsonify({"msg": f"User id: {current_user.id} is not authorized to fetch user id: {user_id} books"}), 401
    query = text("""
    SELECT * FROM books WHERE owner_id = :p
    ORDER BY created_at DESC
    """)

    response = send_query_to_database(query, {'p': user_id})

    if not response:
        return jsonify([]), 200
    # books = db.session.execute(db.select(Book).where(Book.owner_id == user_id)).scalars()
    return jsonify(response), 200


@book_blueprint.route('/reserved_books/<int:user_id>')
@login_required
def get_reserved_books_by_user_id(user_id):
    query = text("""
    SELECT * FROM books
    WHERE
    reserved=TRUE
    AND
    lender_id=:p
    """)

    response = send_query_to_database(query, {'p': user_id})
    return jsonify(response), 200


@user_blueprint.route('/change_duration/<int:user_id>', methods=['PATCH'])
@login_required
def change_duration(user_id):
    pass
    data = request.json
    duration = data.get('duration')
    user = db.get_or_404(User, user_id)
    previous_duration = user.duration

    if current_user.id != user_id:
        return jsonify({"msg": f"Current user id:{current_user.id} cannot change user id: {user_id} duration"}), 401
    try:
        duration = int(duration)
    except (ValueError, TypeError):
        return jsonify({"msg": f"Wrong duration format: {duration}"}), 400

    if not duration or not MIN_LEND_DURATION <= duration <= MAX_LEND_DURATION:
        return jsonify({"message": f"Wrong duration format or value: {duration}"}), 400
    query = text("""
        UPDATE users SET duration = :d
        WHERE id = :id
        """)

    send_query_to_database(query, {'d': int(duration), 'id': user_id})
    # user.duration = duration
    # db.session.commit()
    logger.info(f"User id: {user_id} changed successfully his lending"
                f" period from {previous_duration} days to {duration} days")
    return jsonify({"message": f"Successfully changed user id: {user_id} book lending duration to {duration}"}), 200


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
    pass
    book = db.get_or_404(Book, book_id)
    if current_user.id not in (book.owner_id, book.lender_id):
        return jsonify({"message": f"Unauthorized to return book id {book_id}"}), 401
    query = text("""UPDATE books 
    SET 
    return_date = NULL,
    reserved = FALSE,
    lender_id = NULL,
    lent_out = FALSE
    WHERE id = :id
    """)
    send_query_to_database(query, {'id': book_id})
    # book.return_date = None
    # book.reserved = False
    # book.lender_id = None
    # book.lent_out = False
    # db.session.commit()
    logger.info(f"User id: {current_user.id} returned book {book.title} (id: {book.id}) successfully to it's owner")
    return jsonify({"message": f"Book id {book_id} returned successfully"}), 200


@book_blueprint.route('/activity/<int:book_id>', methods=['PATCH'])
@login_required
def book_activity_toggle(book_id):
    """Activate or deactivate your own book for lending out."""
    pass
    book = db.get_or_404(Book, book_id)
    if book.owner_id != current_user.id:
        return jsonify({"msg": f"Current user id: {current_user.id} cannot change book id {book.id} activity toggle."
                               f"Book owner id: {book.owner_id}"}), 401
    if not book.lent_out:
        query = text("""UPDATE books SET active = :activation
        WHERE id = :book_id""")
        send_query_to_database(query, {'activation': not book.active, 'book_id': book_id})
        #     book.active = not book.active
        #     db.session.commit()
        logger.info(f"(Book id: {book.id}) activity set to {book.active}")
        return jsonify({"message": f"Book availability: {book.active}",
                        "data": book.active}), 200
    return jsonify(success=False, error="Unable to switch book activity toggle."), 400


@book_blueprint.route('/reserve_book/<int:book_id>', methods=['PATCH'])
@login_required
def reserve_book(book_id):
    """
    Reserve book if it's not reserved yet.

    :param book_id: Book.id
    :return: redirect to home page
    """
    book = db.get_or_404(Book, book_id)
    if not book:
        return jsonify({"message": f"Cannot find the book by id: {book_id}"}), 400
    if book.owner_id == current_user.id:
        return jsonify({"message": "Book owner cannot reserve own book"}), 400
    if book.reserved:
        logger.info(f"Failed to reserve book {book_id}")
        return jsonify({"message": f"Failed to reserve book {book_id}"}), 400

    query = text("""UPDATE books SET
         reserved = TRUE,
         lender_id = :lender_id
         WHERE id = :book_id
         """)

    params = {
        "book_id": book.id,
        "lender_id": current_user.id
    }
    send_query_to_database(query, params)
    #     book.reserved = True
    #     book.lender_id = current_user.id
    #     db.session.commit()

    logger.info(f"User id: {current_user.id} reserved book id: {book.id} successfully")
    return jsonify({"message": f"Book id: {book_id} reserved successfully to lender id: {current_user.id}"}), 200


@book_blueprint.route('/cancel_reservation/<int:book_id>', methods=['PATCH'])
@login_required
def cancel_reservation(book_id):
    """Validate that current user is book lender or book owner and cancel the reservation."""
    book = db.get_or_404(Book, book_id)
    message = f"Failed to cancel book id {book_id} reservation"
    if not book.reserved:
        message = f"Book reservation cancellation FAILED, Book id: {book_id}. Book is not reserved"
        logger.error(message)
        return jsonify({"msg": message}), 400
    if book.reserved and (book.owner_id == current_user.id or book.book_lender.id == current_user.id):
        query = text("""UPDATE books SET
        reserved=FALSE,
        lender_id=NULL
        WHERE 
        id=:id
        """)
        send_query_to_database(query, {'id': book_id})
        #     book.reserved = False
        #     book.book_lender = None
        #     db.session.commit()
        message = f"Successfully cancelled book id {book_id} reservation"
        logger.info(message)
        return jsonify({"message": message}), 200
    logger.error(message)
    return jsonify({"message": message}), 401


@book_blueprint.route('/receive_book/<int:book_id>', methods=['PATCH'])
@login_required
def receive_book(book_id):
    """
    Validate book and mark book as handed over to lender.

    :param book_id: Book.id
    :return: redirect to my_reserved_books page
    """
    book = db.get_or_404(Book, book_id)
    if book.lent_out:
        message = f"Book id {book_id} is already lent out"
        logger.info(message)
        return jsonify({"message": message}), 400
    if current_user in (book.book_owner, book.book_lender):
        current_date = datetime.now().date()
        book_owner = db.get_or_404(User, book.owner_id)
        return_date = current_date + timedelta(days=book_owner.duration)
        query = text("""UPDATE books SET
         return_date = :return_date,
         lent_out = TRUE
         WHERE id = :id
        """)
        send_query_to_database(query, {'return_date': return_date, 'id': book_id})
        #         book.return_date = return_date
        #         book.lent_out = True
        #         db.session.commit()
        message = f"Book id {book_id} received successfully"
        logger.info(message)
        return jsonify({"message": message, "returnDate": return_date.strftime("%d-%m-%Y")}), 200
    message = f"Unauthorized to receive book id {book_id}"
    logger.info(message)
    return jsonify({"message": message}), 401


@book_blueprint.route('/remove_book/<int:book_id>', methods=['DELETE'])
@login_required
def remove_book(book_id):
    """Remove a book from the database. Validate that book is not lent out and user is the owner of the book."""
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
    query = text("""DELETE FROM books WHERE id = :id""")
    send_query_to_database(query, {'id': book_id})
    # db.session.delete(book)
    # db.session.commit()
    logger.info(msg)
    return jsonify({"message": msg}), 200


@book_blueprint.route('/add_new_book', methods=['POST'])
@login_required
def add_book():
    """Create and add a new book to the database and lending environment."""
    data = request.json
    title = data.get('title').title()
    author = data.get('author').title()
    image_url = data.get('imageUrl')
    description = data.get('description')

    if len(author) < 4:
        return jsonify({"msg": f"Author value: {author} is too short."}), 400

    if not validate_image_url(image_url):
        return jsonify({"msg": f"Book {title} image URL is invalid"}), 409

    # existing_book = Book.query.filter(
    #     db.func.lower(Book.title) == title.lower(),
    #     db.func.lower(Book.author) == author.lower()
    # ).first()
    existing_book_query = text("""SELECT * FROM books
    WHERE
    title = :title
    AND
    author = :author
    """)
    existing_book = send_query_to_database(existing_book_query, {'title': title, 'author': author})

    if existing_book:
        msg = f"Book {title} already exists in database"
        logger.info(msg)
        return jsonify({"msg": msg}), 409

    add_book_query = text("""INSERT INTO books 
    (title,
    author,
    image_url,
    return_date,
    reserved,
    lent_out,
    owner_id,
    active,
    description)
    VALUES (
    :title,
    :author,
    :image_url,
    NULL,
    FALSE,
    FALSE,
    :owner_id,
    TRUE,
    :description)
    RETURNING id, title, author, image_url, return_date, reserved, lent_out, owner_id, active, description
    """)
    response = send_query_to_database(add_book_query, {'title': title,
                                                       'author': author,
                                                       'image_url': image_url,
                                                       'owner_id': current_user.id,
                                                       'description': description})
    # book_data = response[0]
    print(response[0])
    new_book = Book(title=title,
                    author=author,
                    image_url=image_url,
                    return_date=None,
                    reserved=False,
                    lent_out=False,
                    owner_id=current_user.id,
                    active=True,
                    description=description)
    # db.session.add(new_book)
    # db.session.commit()
    msg = f"New book: {title} added successfully."
    logger.info(msg)
    return jsonify({"message": msg, "data": new_book.to_dict()}), 201


@user_blueprint.route('/current_user', methods=['GET'])
def get_current_user():
    if current_user.is_authenticated:
        return jsonify(User.get_user_dict(current_user)), 200
    return jsonify({"authenticated": False}), 401


@user_blueprint.route('/register', methods=['POST'])
def register():
    """
    Register new user to environment.

    Save new user data to db and login user.
    """
    data = request.json

    first_name = data.get('firstName')
    last_name = data.get('lastName')
    email = data.get('email').lower()
    password = data.get('password')
    msg = "Reading new user data failed"
    if not first_name or not last_name or not email or not password:
        logger.info(msg)
        return jsonify({"message": msg}), 400
    # existing_mail = db.session.execute(db.select(User).where(User.email == email)).scalar()
    query = text("""SELECT * FROM users WHERE email = :email""")
    existing_mail = send_query_to_database(query, {'email': email})
    if existing_mail:
        msg = f"User with email: {email} has already registered. Registration FAILED"
        logger.info(msg)
        return jsonify({"message": msg}), 409


    query = text("""INSERT INTO users (first_name, last_name, email, password)
    VALUES (
    :first_name,
    :last_name,
    :email,
    :password)
    RETURNING id, first_name, last_name, password, email, duration
    """)

    response = send_query_to_database(query, {'first_name': first_name.title(),
                                              'last_name': last_name.title(),
                                              'email': email.lower(),
                                              'password': generate_password_hash(
                                                  password,
                                                  method='pbkdf2:sha256',
                                                  salt_length=8
                                              )})
    user_data = response[0]
    new_user = User(
        id=user_data.get('id'),
        first_name=user_data.get('first_name'),
        last_name=user_data.get('last_name'),
        email=user_data.get('email'),
        password=user_data.get('password'),
        duration=user_data.get('duration'))
    # db.session.add(new_user)
    # db.session.commit()
    login_user(new_user)

    response_data = {
        "id": current_user.id,
        "name": first_name.title(),
        "email": email,
        "duration": DEFAULT_LEND_DURATION
    }
    msg = f"Registered new user id: {current_user.id}!"
    logger.info(msg)
    return jsonify({"message": msg, "data": response_data}), 201


@user_blueprint.route('/login', methods=['POST'])
def login():
    """Validate user username and password to log user in."""
    data = request.json
    if not data:
        logger.info("Login failure")
        return jsonify({"message": "Data receiving failed"}), 400

    email = data.get('email')
    password = data.get('password')

    #     user = db.session.execute(db.select(User).where(User.email == email)).scalar()
    query = text("""SELECT * FROM users WHERE email = :email""")
    response = send_query_to_database(query, {'email': email})

    if not response:
        return jsonify({"message": "Please check your email"}), 401
    user_data = response[0]

    if not check_password_hash(user_data.get('password', ''), password):
        return jsonify({"message": "Please check your password"}), 401
    user = User(
        id=user_data.get('id'),
        first_name=user_data.get('first_name'),
        last_name=user_data.get('last_name'),
        email=user_data.get('email'),
        password=user_data.get('password'),
        duration=user_data.get('duration')
        )

    login_user(user)
    logger.info(f"User id: {user.id} logged in")
    return jsonify({"message": "Successfully logged in",
                    "id": user.id,
                    "name": user.first_name,
                    "email": user.email,
                    "duration": user.duration}), 202


@user_blueprint.route('/logout', methods=['POST'])
@login_required
def logout():
    """Logout current user and redirect to home page."""
    msg = f'User id: {current_user.id} logged out'
    logout_user()
    logger.info(msg)
    return jsonify({'message': msg, 'authenticated': current_user.is_authenticated}), 200
