from functools import wraps

from models.book import Book


def serialize_book(func):
    """Format tuple to list of Book class objects."""
    @wraps(func)
    def formatter(*args, **kwargs):
        for a in func(*args, **kwargs):
            for c in a:
                print(c)
        books = [Book(id=book[0],
                      title=book[1],
                      author=book[2],
                      description=book[3],
                      image_url=book[4],
                      return_date=book[5],
                      reserved=bool(book[6]),
                      lent_out=bool(book[7]),
                      active=bool(book[8]),
                      owner_id=book[9],
                      lender_id=book[10]
                      ) for book in func(*args, **kwargs)]
        return books
    return formatter
