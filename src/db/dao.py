from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv
import os

from src.logger.logger_config import logger

load_dotenv()


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


def init_database(app):
    """Initialize database."""
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
    if not db_uri:
        raise RuntimeError("Cannot find SQLALCHEMY_DATABASE_URI in app config")

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        with app.app_context():
            logger.info("Database initialized with connection pool!")
            try:
                db.engine.connect()
                logger.info("Database connected!")
            except Exception as e:
                logger.error(f"Database connection failed: {e}")
