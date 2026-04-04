from flask_cors import CORS

from src.api.user.controller import user_blueprint
from src.api.book.controller import book_blueprint


CORS(user_blueprint, supports_credentials=True, origins=["http://127.0.0.1:8080"])
CORS(book_blueprint, supports_credentials=True, origins=["http://127.0.0.1:8080"])
