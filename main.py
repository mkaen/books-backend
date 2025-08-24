from flask import Flask
from dotenv import load_dotenv
import os
import logging
from src.db.database import db
from src.api.controller import user_blueprint, book_blueprint
from src.utilities.auth import login_manager
from logger.logger_config import logger, file_handler, formatter

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

    file_handler.setFormatter(logging.Formatter(formatter))
    logger.addHandler(file_handler)

    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config.update({
        'SESSION_COOKIE_NAME': 'session_id'
    })

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
