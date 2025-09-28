from flask_login import current_user
from werkzeug.security import check_password_hash

from db.database import db
from models.user import User
from conf_test import client, first_user_with_books
from test_constants import UserEndpoints, TestUserEmail


def test_register_new_user(client):
    response = client.post(UserEndpoints.REGISTER, json={
        'firstName': 'Priit',
        'lastName': 'pätt',
        'email': 'priit.patt@gmail.com',
        'password': '123456'
    })
    assert response.status_code == 201
    result = db.session.execute(db.select(User).where(User.email == 'priit.patt@gmail.com')).first()
    user = result[0] if result else None
    assert user is not None
    assert user.first_name == 'Priit'
    assert user.last_name == 'Pätt'
    assert user.email == 'priit.patt@gmail.com'
    assert user.duration == 28
    assert check_password_hash(user.password, '123456')
    assert user.password != '123456'


def test_register_email_already_exists(client, first_user_with_books):
    response = client.post(UserEndpoints.REGISTER, json={
        'firstName': 'Juhan',
        'lastName': 'Viik',
        'email': 'juhan.viik@gmail.com',
        'password': '123456'
    })
    assert response.status_code == 409
    with client.session_transaction() as session:
        assert '_user_id' not in session


def test_login_user(client, first_user_with_books):
    response = client.post(UserEndpoints.LOGIN, json={
        'email': TestUserEmail.JUHAN,
        'password': '123456'
    })
    assert current_user.is_authenticated
    with client.session_transaction() as session:
        assert '_user_id' in session
    assert response.status_code == 202


def test_invalid_email_login(client, first_user_with_books):
    response = client.post(UserEndpoints.LOGIN, json={
        'email': 'juhani.viik@gmail.com',
        'password': '123456'
    })
    assert response.status_code == 401
    with client.session_transaction() as session:
        assert '_user_id' not in session


def test_invalid_password_login(client, first_user_with_books):
    response = client.post(UserEndpoints.LOGIN, json={
        'email': TestUserEmail.JUHAN,
        'password': '1234567'
    })
    assert response.status_code == 401


def test_logout_user(client, first_user_with_books):
    login_response = client.post(UserEndpoints.LOGIN, json={
        'email': TestUserEmail.JUHAN,
        'password': '123456'
    })
    assert login_response.status_code == 202
    assert current_user.is_active
    client.post(UserEndpoints.LOGOUT)
    assert not current_user.is_authenticated
    with client.session_transaction() as session:
        assert '_user_id' not in session


def test_logout_user_not_in_session(client):
    response = client.get(UserEndpoints.LOGOUT)
    assert response.status_code == 405
