from flask_cors import CORS

from src.api.user.controller import user_blueprint
from src.api.book.controller import book_blueprint
from dotenv import load_dotenv
import os

load_dotenv()
FRONTEND_URL = os.getenv('FRONTEND_URL')

CORS(user_blueprint, supports_credentials=True, origins=[FRONTEND_URL])
CORS(book_blueprint, supports_credentials=True, origins=[FRONTEND_URL])
