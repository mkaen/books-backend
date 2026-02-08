from flask import Flask
import os
import logging

from src.db.dao import init_database
from src.db.health import check_database

from src.api.controller import user_blueprint, book_blueprint
from src.utilities.auth import login_manager
from src.configuration.config import Configuration
from src.logger.logger_config import logger, configure_logger


def create_app(test_config=None):
    """Create and start Flask application."""
    app = Flask(__name__)

    app.config.from_object(Configuration)
    configure_logger()
    if test_config:
        app.config.from_object(test_config)
    else:
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_size': 5,
            'max_overflow': 10,
            'pool_pre_ping': True,
            'pool_recycle': 3600
        }

    # DATABASE
    init_database(app)
    # To minimize db connections
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        with app.app_context():
            check_database()

    # AUTHORIZATION
    login_manager.init_app(app)

    # BLUEPRINTS
    app.register_blueprint(user_blueprint)
    app.register_blueprint(book_blueprint)

    @app.route('/health')
    def health():
        """Check database health."""
        with app.app_context():
            db_ok = check_database()
        return {
            'status': 'Healthy' if db_ok else 'degraded',
            'database': 'Connected' if db_ok else 'tables missing'
        }, 200 if db_ok else 503

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5001)
