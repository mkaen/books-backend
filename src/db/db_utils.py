import os.path
import sqlite3
from flask import current_app as app

from db.decorator import serialize_book


def get_database_path():
    uri = app.config.get('SQLALCHEMY_DATABASE_URI')
    if uri.startswith('sqlite:///'):
        path = uri.replace('sqlite:///', '')
        if not os.path.isabs(path):
            path = os.path.join(os.path.dirname(__file__), '../instance', path)
            path = os.path.abspath(path)
            return path


@serialize_book
def fetch_books():
    con = sqlite3.connect(get_database_path())
    cur = con.cursor()
    cur.execute('''SELECT * FROM books''')
    result = cur.fetchall()
    con.close()
    return result


@serialize_book
def fetch_user_books(user_id):
    con = sqlite3.connect(get_database_path())
    cur = con.cursor()
    cur.execute('''SELECT * FROM books WHERE owner_id = :p''', (user_id, ))
    result = cur.fetchall()
    con.close()
    return result
