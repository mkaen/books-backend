from db.database import db
from models.user import User
from models.book import Book
from conf_test import client, first_user_with_books, second_user_with_books
from auth_helper import login
from test_constants import TestUserEmail, BookEndpoints

cashflow = {
    'title': "Rich Dad's CASHFLOW Quadrant: Rich Dad's Guide to Financial Freedom",
    'author': 'Robert Kiyosaki',
    'imageUrl': 'https://m.media-amazon.com/images/I/71+SWQ6xj1L._SY466_.jpg',
    'description': 'Cashflow description'
}
rich_dad = {
    'title': 'Rich Dad Poor Dad',
    'author': 'Robert Kiyosaki',
    'imageUrl': 'https://upload.wikimedia.org/wikipedia/en/thumb/b/b9/Rich_Dad_Poor_Dad.jpg/220px-Rich_Dad_Poor_Dad.jpg',
    'description': 'First book'
}


def test_users_amount_in_temporary_db(client, first_user_with_books, second_user_with_books):
    users = User.query.all()
    assert len(users) == 2


def test_books_amount_in_temporary_db(client, first_user_with_books, second_user_with_books):
    books = Book.query.all()
    assert len(books) == 4


def test_validate_book_ownership(client, first_user_with_books, second_user_with_books):
    book_rich_dad = db.session.query(Book).filter(Book.title.ilike(rich_dad.get('title'))).first()
    assert book_rich_dad.owner_id == 1
    rd_book_owner = db.get_or_404(User, 1)
    assert rd_book_owner.last_name == 'Viik'
    book_hp = db.session.query(Book).filter(Book.title.ilike("Harry Potter and the Sorcerer's Stone")).first()
    assert book_hp.owner_id == 2
    hp_book_owner = db.get_or_404(User, 2)
    assert hp_book_owner.first_name == 'Priit'


def test_add_book(client, first_user_with_books):
    """Test adding a book after login."""
    login(client, TestUserEmail.JUHAN)
    assert Book.query.count() == 2
    response = client.post(BookEndpoints.ADD_BOOK, json=cashflow)
    assert response.status_code == 201
    assert Book.query.count() == 3
    book = db.session.query(Book).filter(Book.title.ilike(cashflow.get('title'))).first()
    assert book is not None
    assert book.author == cashflow.get('author')


def test_add_book_user_not_authenticated(client):
    """Test add_book if user not logged in."""
    response = client.post(BookEndpoints.ADD_BOOK, json=cashflow)
    assert response.status_code == 401


def test_add_book_title_already_exists(client, first_user_with_books):
    """Test adding a book that already exists in database after login."""
    login_response = login(client, TestUserEmail.JUHAN)
    print(login_response)
    result = db.session.query(Book).filter(Book.title.ilike(rich_dad.get('title'))).all()
    assert len(result) == 1
    response = client.post('/book_api/add_new_book', json=rich_dad)
    assert response.status_code == 409
    result = db.session.query(Book).filter(Book.title.ilike(rich_dad.get('title'))).all()
    assert len(result) == 1


def test_add_book_author_name_too_short(client, first_user_with_books):
    login(client, TestUserEmail.JUHAN)
    response = client.post(BookEndpoints.ADD_BOOK, json={
        'title': 'New book',
        'author': 'R K',
        'imageUrl': 'https://upload.wikimedia.org/wikipedia/en/thumb/b/b9/Rich_Dad_Poor_Dad.jpg/220px'
                    '-Rich_Dad_Poor_Dad.jpg'
    })
    assert response.status_code == 400
    books = db.session.query(Book).all()
    assert len(books) == 2


def test_add_book_wrong_url(client, first_user_with_books):
    login(client, TestUserEmail.JUHAN)
    response = client.post(BookEndpoints.ADD_BOOK, json={
        'title': 'Rich Dad Poor Dad',
        'author': 'R. Kiyosaki',
        'imageUrl': 'https://upload.wikimedia.org/wikipedia'
    })
    assert response.status_code == 409
