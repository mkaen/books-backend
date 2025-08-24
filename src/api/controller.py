from datetime import datetime, timedelta

from flask import request, jsonify
from flask_login import login_required, current_user, logout_user, login_user
from werkzeug.security import generate_password_hash, check_password_hash

from src.constants import MIN_LEND_DURATION, MAX_LEND_DURATION
from src.models import user
from src.models.database import db
from src.models.user import User
from src.models.book import Book
from src.auth.routes import user_blueprint, book_blueprint
from src.utilities.service import validate_image_url
from logger.logger_config import logger


@book_blueprint.route('/fetch_books')
def get_all_the_books():
    books = Book.query.all()
    book_list = [book.to_dict() for book in books]
    return jsonify(book_list), 200


@user_blueprint.route('/change_duration/<int:user_id>', methods=['PATCH'])
@login_required
def change_duration(user_id):
    data = request.json
    duration = int(data.get('duration'))
    user = db.get_or_404(User, user_id)
    if not duration or not MIN_LEND_DURATION <= duration <= MAX_LEND_DURATION:
        return jsonify({"message": f"Wrong duration format or value: {duration}"}), 400
    user.duration = duration
    db.session.commit()
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
    book = db.get_or_404(Book, book_id)
    if current_user.id not in (book.owner_id, book.lender_id):
        return jsonify({"message": f"Unauthorized to return book id {book_id}"}), 401
    book.return_date = None
    book.reserved = False
    book.lender_id = None
    book.lent_out = False
    db.session.commit()
    return jsonify({"message": f"Book id {book_id} returned successfully"}), 200


@book_blueprint.route('/activity/<int:book_id>', methods=['PATCH'])
@login_required
def book_activity_toggle(book_id):
    """Activate or deactivate your own book for lending out."""
    book = db.get_or_404(Book, book_id)
    if book and book.owner_id == current_user.id and book.lent_out is False:
        book.active = not book.active
        db.session.commit()
        logger.info(f"(Book id: {book.id}) activity set to {book.active}")
        return jsonify({"message": f"Book availability: {book.active}",
                        "data": book.active}), 200
    return jsonify(success=False, error="You are not authorized to do that action."), 401


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
    if not book.reserved:
        book.reserved = True
        book.lender_id = current_user.id
        db.session.commit()
        response_data = {
            "id": book.id,
            "lenderId": current_user.id
        }
        return jsonify({"message": f"Book id: {book_id} reserved successfully to lender id: {current_user.id}",
                        "data": response_data}), 200
    logger.info(f"Failed to reserve book {book_id}")
    return jsonify({"message": f"Failed to reserve book {book_id}"}), 400


@book_blueprint.route('/cancel_reservation/<int:book_id>', methods=['PATCH'])
@login_required
def cancel_reservation(book_id):
    """Validate that current user is book lender or book owner and cancel the reservation."""
    book = db.get_or_404(Book, book_id)
    message = f"Failed to cancel book id {book_id} reservation"
    if book.reserved and (book.owner_id == current_user.id or book.book_lender.id == current_user.id):
        book.reserved = False
        book.book_lender = None
        db.session.commit()
        message = f"Successfully cancelled book id {book_id} reservation"
        logger.info(message)
        return jsonify({"message": message}), 200
    logger.info(message)
    return jsonify({"message": message}), 400


@book_blueprint.route('/receive_book/<int:book_id>', methods=['PATCH'])
@login_required
def receive_book(book_id):
    """
    Validate book and mark book as handed over to lender.

    :param book_id: Book.id
    :return: redirect to my_reserved_books page
    """
    book = db.get_or_404(Book, book_id)
    message = f"Book id {book_id} received successfully"
    if not book.lent_out:
        if current_user in (book.book_owner, book.book_lender):
            user = db.get_or_404(User, current_user.id)
            current_date = datetime.now().date()
            return_date = current_date + timedelta(days=user.duration)
            book.return_date = return_date
            book.lent_out = True
            db.session.commit()
            logger.info(message)
            return jsonify({"message": message, "returnDate": return_date.strftime("%d-%m-%Y")})
        message = f"Unauthorized to receive book id {book_id}"
        logger.info(message)
        return jsonify({"message": message}), 401
    message = f"Book id {book_id} is already lent out"
    logger.info(message)
    return jsonify({"message": message})


@book_blueprint.route('/remove_book/<int:book_id>', methods=['DELETE'])
@login_required
def remove_book(book_id):
    """Remove a book from the database. Validate that book is not lent out and user is the owner of the book."""
    book = db.get_or_404(Book, book_id)
    msg = f"Book id {book_id} removed successfully from database"
    if current_user.id != book.owner_id:
        msg = "Book cannot remove by non book owner"
        logger.info(msg)
        return jsonify({"message": msg}), 401
    if book.lent_out or book.reserved:
        msg = "Cannot remove book while it's reserved or lent out"
        logger.info(msg)
        return jsonify({"message": msg}), 400
    db.session.delete(book)
    db.session.commit()
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

    if not validate_image_url(image_url):
        return jsonify({"msg": f"Book {title} image URL is invalid"}), 409

    existing_book = Book.query.filter(
        db.func.lower(Book.title) == title.lower(),
        db.func.lower(Book.author) == author.lower()
    ).first()
    if existing_book:
        msg = f"Book {title} already exists in database"
        logger.info(msg)
        return jsonify({"msg": msg}), 409
    new_book = Book(title=title,
                    author=author,
                    image_url=image_url,
                    return_date=None,
                    reserved=False,
                    lent_out=False,
                    owner_id=current_user.id,
                    active=True,
                    description=description)
    db.session.add(new_book)
    db.session.commit()
    msg = f"New book: {title} added successfully."
    logger.info(msg)
    return jsonify({"message": msg, "data": new_book.to_dict()}), 201


@user_blueprint.route('/current_user', methods=['GET'])
def get_current_user():
    if current_user.is_authenticated:
        return jsonify(user.User.get_user_dict(current_user)), 200
    logger.info(f"Current user is unauthorized user")
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
    email = data.get('email')
    password = data.get('password')
    msg = "Reading new user data failed"
    if not first_name or not last_name or not email or not password:
        logger.info(msg)
        return jsonify({"message": msg}), 400
    existing_mail = db.session.execute(db.select(User).where(User.email == email)).scalar()
    if existing_mail:
        msg = f"User with email: {email} has already registered"
        logger.info(msg)
        return jsonify({"message": msg}), 409
    new_user = User(first_name=first_name.title(),
                    last_name=last_name.title(),
                    email=email,
                    password=generate_password_hash(
                        password,
                        method='pbkdf2:sha256',
                        salt_length=8
                    ))
    db.session.add(new_user)
    db.session.commit()
    login_user(new_user)

    response_data = {
        "id": current_user.id,
        "name": first_name.title(),
        "email": email,
        "duration": 28
    }
    msg = f"Registered new user id: {current_user.id}!"
    logger.info(msg)
    return jsonify({"message": msg, "data": response_data}), 201


@user_blueprint.route('/login', methods=['POST'])
def login():
    """Validate user username and password to log user in."""
    data = request.json
    if data:
        email = data.get('email')
        password = data.get('password')
        user = db.session.execute(db.select(User).where(User.email == email)).scalar()
        if not user:
            return jsonify({"message": "Please check your email"}), 401

        if not check_password_hash(user.password, password):
            return jsonify({"message": "Please check your password"}), 401

        login_user(user)
        logger.info(f"User id: {user.id} logged in successfully")
        return jsonify({"message": "Successfully logged in",
                        "id": user.id,
                        "name": user.first_name,
                        "email": user.email,
                        "duration": user.duration}), 202
    logger.info("Login failure")
    return jsonify({
        "message": "Data receive malfunction"
    }), 400


@user_blueprint.route('/logout', methods=['POST'])
@login_required
def logout():
    """Logout current user and redirect to home page."""
    msg = f'User id: {current_user.id} logged out successfully'
    logout_user()
    return jsonify({'message': msg, 'authenticated': current_user.is_authenticated}), 200
