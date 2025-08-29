from flask import Blueprint
from flask_cors import CORS

user_blueprint = Blueprint('user_api', __name__, url_prefix='/user_api')
book_blueprint = Blueprint('book_api', __name__, url_prefix='/book_api')

CORS(user_blueprint,
     supports_credentials=True,
     origins=["http://127.0.0.1:8080", "http://localhost:8080"],
     resources={r"/*": {"origins": "*"}})
CORS(book_blueprint,
     supports_credentials=True,
     origins=["http://127.0.0.1:8080", "http://localhost:8080"],
     resources={r"/*": {"origins": "*"}})
