from conftest import client, first_user_with_books, second_user_with_books
import src.api.book.service as s
from auth_helper import login
from src.db.dao import db
from src.models.models import Book
from test_constants import TestUserEmail, BookEndpoints


def test_get_all_books(client, first_user_with_books, second_user_with_books):
    books = s.fetch_all_books().get_json()
    print(books)
    assert len(books) == 4
    assert books[0]['title'] == "Harry Potter and the Chamber of Secrets"
    assert books[1]['title'] == "Harry Potter and the Sorcerer's Stone"
    assert books[2]['title'] == "Before You Quit Your Job"
    assert books[3]['title'] == "Rich Dad Poor Dad"


def test_fetch_user_books(client, first_user_with_books, second_user_with_books):
    response, status_code = s.fetch_user_books(2)
    books = response.get_json()

    assert len(books) == 2
    assert status_code == 200

    books_titles = [book['title'] for book in books]
    assert "Harry Potter and the Chamber of Secrets" in books_titles
    assert "Harry Potter and the Sorcerer's Stone" in books_titles


def test_fetch_user_books_no_books(client, first_user_with_books, third_user_without_books):
    response, status_code = s.fetch_user_books(2)
    books = response.get_json()

    assert len(books) == 0
    assert status_code == 200


def test_fetch_user_reserved_books(client, first_user_with_books, third_user_without_books):
    login(client, TestUserEmail.TOOMAS)
    response = client.patch(f'{BookEndpoints.RESERVE_BOOK}/1')
    book = db.get_or_404(Book, 1)
    assert response.status_code == 200
    assert book.reserved


def test_fetch_user_reserved_books_no_books(client, first_user_with_books, third_user_without_books):
    login(client, TestUserEmail.TOOMAS)
    books, status_code = s.fetch_user_reserved_books(2)
    assert status_code == 200
    assert books.get_json() == []
