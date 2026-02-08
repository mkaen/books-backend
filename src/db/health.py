from sqlalchemy import text
from src.logger.logger_config import logger
from src.db.dao import db
from src.constants import DB_TABLES


def check_database():
    """Check tables existent in database."""
    try:
        result = db.session.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = ANY(:tables)
                """), {'tables': list(DB_TABLES)})

        tables = {row[0] for row in result}
        missing = DB_TABLES - tables

        if missing:
            logger.warning(f"Missing tables: {missing}. Run: alembic upgrade head!")
            return False

        logger.info(f"Validated database tables: {DB_TABLES}.")
        return True

    except Exception as e:
        logger.error(f"Database error: {e}")
        return False
