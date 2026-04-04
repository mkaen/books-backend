from src.db.dao import db
from src.logger.logger_config import logger
from src.models.models import Book


def send_query_to_database(query, params=None):
    """Execute SQL query."""
    result = db.session.execute(query, params or {})

    query = str(query).upper().strip()

    if query.startswith('SELECT'):
        data = [dict(row._mapping) for row in result]
        return data
    elif 'RETURNING' in query:
        db.session.commit()
        data = [dict(row._mapping) for row in result]
        logger.debug(f"Successful query: {str(query)}")
        return data
    else:
        db.session.commit()
        logger.debug(f"Successful query: {str(query)}")
        return result.rowcount


def serialize_to_list_of_books(data):
    book_list = []
    for row in data:
        row = dict(row)
        book = Book(
            id=row.get('id'),
            title=row.get('title'),
            author=row.get('author'),
            description=row.get('description'),
            image_url=row.get('image_url'),
            reserved=row.get('reserved'),
            lent_out=row.get('lent_out'),
            active=row.get('active'),
            owner_id=row.get('owner_id'),
            lender_id=row.get('lender_id'),
            return_date=row.get('return_date')
        )
        book_list.append(book)

    return book_list
