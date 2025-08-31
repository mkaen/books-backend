from flask import Flask
from dotenv import load_dotenv
import os
import logging
from src.db.database import db
from src.api.controller import user_blueprint, book_blueprint
from src.utilities.auth import login_manager
from logger.logger_config import logger

load_dotenv()

DATABASE = os.environ.get('DATABASE')
SECRET_KEY = os.environ.get('SECRET_KEY')
LOGGER_TEST = os.environ.get('LOGGER_TEST')


def create_app(config_class=None):
    """Create and configure Flask application."""
    app = Flask(__name__)

    if config_class:
        app.config.from_object(config_class)
        logger.file_handler = logging.FileHandler(LOGGER_TEST, mode="w")
        logger.setLevel(logging.DEBUG)

    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_NAME'] = 'session_id'
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_SECURE'] = False

    db.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(user_blueprint)
    app.register_blueprint(book_blueprint)

    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5001)
