from datetime import datetime, timedelta
import logging

from flask_login import current_user

from main import db
from models.user import User
from models.book import Book
from conf_test import client, first_user_with_books, second_user_with_books, third_user_with_books
from auth_helper import login, logout
from test_constants import TestUserEmail, BookEndpoints
from test_utils import reserve_and_receive_book


# RESERVATION
def test_reserve_book(client, first_user_with_books, second_user_with_books):
    login(client, TestUserEmail.JUHAN)
    book = db.get_or_404(Book, 3)
    assert not book.reserved
    response = client.patch(f'{BookEndpoints.RESERVE_BOOK}/3')
    book = db.get_or_404(Book, 3)
    assert response.status_code == 200
    assert book.reserved


def test_reserve_book_not_found(client, first_user_with_books):
    login(client, TestUserEmail.JUHAN)
    response = client.patch(f'{BookEndpoints.RESERVE_BOOK}/3')
    assert response.status_code == 404


def test_reserve_book_already_reserved(client, first_user_with_books, second_user_with_books, third_user_with_books):
    login(client, TestUserEmail.TOOMAS)
    response = client.patch(f'{BookEndpoints.RESERVE_BOOK}/1')
    book = db.get_or_404(Book, 1)
    assert response.status_code == 200
    assert book.reserved
    assert book.lender_id == 3
    logout(client)
    login(client, TestUserEmail.PRIIT)
    client.patch(f'{BookEndpoints.RESERVE_BOOK}/1')
    updated_book = db.get_or_404(Book, 1)
    assert updated_book.lender_id != current_user.id


def test_reserve_book_user_not_authenticated(client, first_user_with_books):
    response = client.patch(f'{BookEndpoints.RESERVE_BOOK}/1')
    assert response.status_code == 401


def test_reserve_book_reserve_own_book(client, first_user_with_books):
    login(client, TestUserEmail.JUHAN)
    book = db.get_or_404(Book, 1)
    assert not book.reserved
    response = client.patch(f'{BookEndpoints.RESERVE_BOOK}/{book.id}')
    updated_book = db.get_or_404(Book, 1)
    assert response.status_code == 400
    assert not updated_book.reserved


#  BOOK CANCELLATION
def test_cancel_reservation_by_owner(client, first_user_with_books, third_user_with_books):
    login(client, TestUserEmail.TOOMAS)
    reservation_response = client.patch(f'{BookEndpoints.RESERVE_BOOK}/1')
    assert reservation_response.status_code == 200
    book = db.get_or_404(Book, 1)
    assert book.reserved
    assert book.lender_id == 2
    user = db.get_or_404(User, 2)
    assert book.book_lender == user
    logout(client)
    login(client, TestUserEmail.JUHAN)
    cancel_response = client.patch(f'{BookEndpoints.CANCEL_RESERVATION}/{book.id}')
    updated_book = db.get_or_404(Book, 1)
    assert cancel_response.status_code == 200
    assert not updated_book.reserved
    assert not updated_book.lender_id
    assert not updated_book.book_lender


def test_cancel_reservation_by_lender(client, first_user_with_books, third_user_with_books):
    login(client, TestUserEmail.TOOMAS)
    reservation_response = client.patch(f'{BookEndpoints.RESERVE_BOOK}/1')
    assert reservation_response.status_code == 200
    book = db.get_or_404(Book, 1)
    assert book.reserved
    cancel_response = client.patch(f'{BookEndpoints.CANCEL_RESERVATION}/{book.id}')
    updated_book = db.get_or_404(Book, 1)
    assert cancel_response.status_code == 200
    assert not updated_book.reserved


def test_cancel_reservation_by_not_authenticated_user(client, first_user_with_books):
    reservation_response = client.patch(f'{BookEndpoints.CANCEL_RESERVATION}/1')
    assert reservation_response.status_code == 401


def test_cancel_reservation_by_unauthorized_user(client, first_user_with_books, second_user_with_books,
                                                 third_user_with_books):
    login(client, TestUserEmail.PRIIT)
    reservation_response = client.patch(f'{BookEndpoints.RESERVE_BOOK}/1')
    assert reservation_response.status_code == 200
    logout(client)
    login(client, TestUserEmail.TOOMAS)
    response = client.patch(f'{BookEndpoints.CANCEL_RESERVATION}/1')
    assert response.status_code == 401


def test_cancel_reservation_own_book_not_reserved(client, first_user_with_books, caplog):
    with caplog.at_level(logging.WARNING):
        login(client, TestUserEmail.JUHAN)
        response = client.patch(f'{BookEndpoints.CANCEL_RESERVATION}/1')
        assert response.status_code == 400
        assert "Cannot cancel reservation Book id: 1 Book wasn't reserved" in caplog.text


def test_cancel_reservation_book_not_found(client, first_user_with_books):
    login(client, TestUserEmail.JUHAN)
    response = client.patch(f'{BookEndpoints.CANCEL_RESERVATION}/3')
    assert response.status_code == 404


# RECEIVE BOOK

def test_receive_book_by_lender(client, first_user_with_books, third_user_with_books):
    login(client, TestUserEmail.TOOMAS)
    client.patch(f'{BookEndpoints.RESERVE_BOOK}/1')
    response = client.patch(f'{BookEndpoints.RECEIVE_BOOK}/1')
    book = db.get_or_404(Book, 1)
    assert response.status_code == 200
    assert book.lent_out
    assert book.return_date


def test_receive_book_by_borrower(client, first_user_with_books, third_user_with_books):
    login(client, TestUserEmail.TOOMAS)
    client.patch(f'{BookEndpoints.RESERVE_BOOK}/1')
    logout(client)
    login(client, TestUserEmail.JUHAN)
    response = client.patch(f'{BookEndpoints.RECEIVE_BOOK}/1')
    assert response.status_code == 200
    book = db.get_or_404(Book, 1)
    assert book.lent_out
    assert book.reserved
    assert book.return_date
    assert book.lender_id == 2


def test_receive_book_user_not_authenticated(client, first_user_with_books, third_user_with_books):
    login(client, TestUserEmail.TOOMAS)
    client.patch(f'{BookEndpoints.RESERVE_BOOK}/1')
    logout(client)
    response = client.patch(f'{BookEndpoints.RECEIVE_BOOK}/1')
    assert response.status_code == 401


def test_receive_book_user_unauthorized(client, first_user_with_books, second_user_with_books, third_user_with_books):
    login(client, TestUserEmail.TOOMAS)
    client.patch(f'{BookEndpoints.RESERVE_BOOK}/1')
    logout(client)
    login(client, TestUserEmail.PRIIT)
    response = client.patch(f'{BookEndpoints.RECEIVE_BOOK}/1')
    assert response.status_code == 401


def test_receive_book_not_found(client, third_user_with_books):
    login(client, TestUserEmail.TOOMAS)
    response = client.patch(f'{BookEndpoints.RECEIVE_BOOK}/1')
    assert response.status_code == 404


def test_receive_book_already_received(client, third_user_with_books, first_user_with_books):
    login(client, TestUserEmail.TOOMAS)
    reserve_and_receive_book(client, 1)
    response = client.patch(f'{BookEndpoints.RECEIVE_BOOK}/1')
    assert response.status_code == 400


def test_receive_book_set_return_date(client, third_user_with_books, first_user_with_books):
    login(client, TestUserEmail.TOOMAS)
    reserve_and_receive_book(client, 1)
    book = db.get_or_404(Book, 1)
    assert book.return_date == (datetime.now().date() + timedelta(days=28))


#  RETURN BOOK

def test_return_book_by_lender(client, first_user_with_books, third_user_with_books):
    login(client, TestUserEmail.TOOMAS)
    reserve_and_receive_book(client, 1)
    book = db.get_or_404(Book, 1)
    assert book.lender_id
    assert book.reserved
    assert book.lent_out
    assert book.return_date
    assert book.book_lender
    response = client.patch(f'{BookEndpoints.RETURN_BOOK}/1')
    assert response.status_code == 200
    book = db.get_or_404(Book, 1)
    assert not book.lender_id
    assert not book.reserved
    assert not book.lent_out
    assert not book.return_date
    assert not book.book_lender


def test_return_book_by_borrower(client, first_user_with_books, third_user_with_books):
    login(client, TestUserEmail.TOOMAS)
    reserve_and_receive_book(client, 1)
    logout(client)
    login(client, TestUserEmail.JUHAN)
    response = client.patch(f'{BookEndpoints.RETURN_BOOK}/1')
    assert response.status_code == 200
    book = db.get_or_404(Book, 1)
    assert not book.lent_out
    assert not book.reserved
    assert not book.return_date
    assert not book.lender_id


def test_return_book_not_found(client, third_user_with_books):
    login(client, TestUserEmail.TOOMAS)
    response = client.patch(f'{BookEndpoints.RETURN_BOOK}/1')
    assert response.status_code == 404


def test_return_book_user_not_authenticated(client, first_user_with_books):
    response = client.patch(f'{BookEndpoints.RETURN_BOOK}/1')
    assert response.status_code == 401


def test_return_book_user_not_authorized(client, first_user_with_books, second_user_with_books, third_user_with_books):
    login(client, TestUserEmail.TOOMAS)
    reserve_and_receive_book(client, 1)
    logout(client)
    login(client, TestUserEmail.PRIIT)
    response = client.patch(f'{BookEndpoints.RETURN_BOOK}/1')
    assert response.status_code == 401



