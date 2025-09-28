from main import db
from models.user import User
from models.book import Book
from conf_test import client, first_user_with_books, second_user_with_books
from auth_helper import login, logout
from test_constants import TestUserEmail, BookEndpoints, UserEndpoints
from test_utils import reserve_and_receive_book


# BOOK ACTIVATION
def test_deactivate_and_activate_for_lending(client, first_user_with_books):
    login_response = login(client, TestUserEmail.JUHAN)
    assert login_response.status_code == 202
    activated_books = db.session.execute(
        db.session.query(Book).filter(Book.active)).scalars().all()
    assert len(activated_books) == 2
    book = db.get_or_404(Book, 1)
    assert book.active
    activation_response = client.patch(f'{BookEndpoints.BOOK_ACTIVITY}/{book.id}')
    updated_book = db.get_or_404(Book, 1)
    assert updated_book.active is False
    assert activation_response.status_code == 200
    activated_books = db.session.execute(db.session.query(Book)
                                         .filter(Book.active)).scalars().all()
    assert len(activated_books) == 1
    client.patch(f'{BookEndpoints.BOOK_ACTIVITY}/{book.id}')
    updated_book = db.get_or_404(Book, 1)
    assert updated_book.active


def test_cannot_deactivate_book_while_book_is_lent_out(client, first_user_with_books, second_user_with_books):
    login(client, TestUserEmail.JUHAN)
    book = db.get_or_404(Book, 4)
    assert book.active
    reserve_and_receive_book(client, book.id)
    book = db.get_or_404(Book, 4)
    print(book.lent_out)
    logout(client)
    login(client, TestUserEmail.PRIIT)
    client.patch(f'{BookEndpoints.BOOK_ACTIVITY}/{book.id}')
    updated_book = db.get_or_404(Book, 4)
    assert updated_book.active


def test_deactivate_book_while_user_is_anonymous(client, first_user_with_books):
    book = db.get_or_404(Book, 2)
    assert book.active
    response = client.patch(f'{BookEndpoints.BOOK_ACTIVITY}/2')
    book = db.get_or_404(Book, 2)
    assert book.active is True
    assert response.status_code == 401


def test_cannot_deactivate_book_not_owner(client, first_user_with_books, second_user_with_books):
    login(client, TestUserEmail.PRIIT)
    book = db.get_or_404(Book, 1)
    assert book.active
    response = client.patch(f'{BookEndpoints.BOOK_ACTIVITY}/1')
    assert response.status_code == 401
    book = db.get_or_404(Book, 1)
    assert book.active


#  SET USER BORROWING DURATION
def test_set_lending_duration(client, first_user_with_books):
    login(client, TestUserEmail.JUHAN)
    user = db.get_or_404(User, 1)
    assert user.duration == 28
    duration_response = client.patch(f'{UserEndpoints.CHANGE_DURATION}/{user.id}', json={'duration': 12})
    assert duration_response.status_code == 200
    user = db.get_or_404(User, 1)
    assert user.duration == 12


def test_set_lending_duration_too_low(client, first_user_with_books):
    login(client, TestUserEmail.JUHAN)
    user = db.get_or_404(User, 1)
    response = client.patch(f"{UserEndpoints.CHANGE_DURATION}/{user.id}", json={'duration': 6})
    assert response.status_code == 400
    assert user.duration == 28
    response = client.patch(f"{UserEndpoints.CHANGE_DURATION}/{user.id}", json={'duration': -1})
    assert response.status_code == 400
    assert user.duration == 28


def test_set_lending_duration_too_high(client, first_user_with_books):
    login(client, TestUserEmail.JUHAN)
    user = db.get_or_404(User, 1)
    response = client.patch(f"{UserEndpoints.CHANGE_DURATION}/{user.id}", json={'duration': 100})
    assert response.status_code == 400
    assert user.duration == 28


def test_set_duration_user_anonymous(client, first_user_with_books):
    user = db.get_or_404(User, 1)
    assert user.duration == 28
    response = client.patch(f'{UserEndpoints.CHANGE_DURATION}/{user.id}', json={'duration': 12})
    assert response.status_code == 401
    assert user.duration == 28


def test_set_duration_current_user_not_allowed(client, first_user_with_books, second_user_with_books):
    login(client, TestUserEmail.JUHAN)
    response = client.patch(f'{UserEndpoints.CHANGE_DURATION}/2', json={'duration': 12})
    assert response.status_code == 401


def test_set_lending_duration_not_change_borrowed_books(client, first_user_with_books, second_user_with_books):
    login(client, TestUserEmail.PRIIT)
    reserve_and_receive_book(client, 2)
    book = db.get_or_404(Book, 2)
    return_date = book.return_date
    logout(client)
    login(client, TestUserEmail.JUHAN)
    user = db.get_or_404(User, 1)
    assert user.duration == 28
    duration_response = client.patch(f'{UserEndpoints.CHANGE_DURATION}/1', json={'duration': 12})
    assert duration_response.status_code == 200
    book = db.get_or_404(Book, 2)
    assert book.return_date == return_date


def test_set_lending_duration_wrong_input(client, first_user_with_books, second_user_with_books):
    login(client, TestUserEmail.JUHAN)
    user = db.get_or_404(User, 1)
    assert user.duration == 28
    response = client.patch(f'{UserEndpoints.CHANGE_DURATION}/{user.id}', json={'duration': 'a'})
    assert response.status_code == 400
    assert "Wrong duration format" in response.json["msg"]
    user = db.get_or_404(User, 1)
    assert user.duration == 28


# REMOVE BOOK
def test_remove_book(client, first_user_with_books):
    login(client, TestUserEmail.JUHAN)
    user = db.get_or_404(User, 1)
    response = client.delete(f'{BookEndpoints.REMOVE_BOOK}/1')
    assert response.status_code == 200
    user_books = db.session.execute(db.select(Book).where(Book.book_owner == user)).scalars().all()
    assert len(user_books) == 1
    deleted_book = db.session.execute(db.select(Book).where(Book.title == 'Rich Dad Poor Dad')).scalars().all()
    assert not deleted_book


def test_remove_book_wrong_input(client, first_user_with_books):
    wrong_inputs = ['a', '?', '-5']
    login(client, TestUserEmail.JUHAN)
    user = db.get_or_404(User, 1)
    for element in wrong_inputs:
        response = client.delete(f'{BookEndpoints.REMOVE_BOOK}/{element}')
        assert response.status_code == 404
    books = db.session.execute(db.select(Book).where(Book.book_owner == user)).scalars().all()
    assert len(books) == 2


def test_remove_book_lent_out(client, first_user_with_books, second_user_with_books):
    login(client, TestUserEmail.PRIIT)
    reserve_and_receive_book(client, 1)
    logout(client)
    login(client, TestUserEmail.JUHAN)
    response = client.delete(f'{BookEndpoints.REMOVE_BOOK}/1')
    assert response.status_code == 400
    user = db.get_or_404(User, 1)
    books = db.session.execute(db.select(Book).where(Book.book_owner == user)).scalars().all()
    assert len(books) == 2


def test_remove_book_reserved(client, first_user_with_books, second_user_with_books):
    login(client, TestUserEmail.PRIIT)
    client.patch(f'{BookEndpoints.RESERVE_BOOK}/1')
    logout(client)
    login(client, TestUserEmail.JUHAN)
    response = client.delete(f'{BookEndpoints.REMOVE_BOOK}/1')
    user = db.get_or_404(User, 1)
    books = db.session.execute(db.select(Book).where(Book.book_owner == user)).scalars().all()
    assert response.status_code == 400
    assert len(books) == 2


def test_remove_book_not_authenticated_user(client, first_user_with_books):
    response = client.delete(f'{BookEndpoints.REMOVE_BOOK}/1')
    assert response.status_code == 401


def test_remove_book_unauthorized_user(client, first_user_with_books, second_user_with_books):
    login(client, TestUserEmail.PRIIT)
    response = client.delete(f'{BookEndpoints.REMOVE_BOOK}/1')
    assert response.status_code == 401
    book = db.session.execute(db.select(Book).where(Book.id == 1)).scalars().first()
    assert book
