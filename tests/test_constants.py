class TestUserEmail:
    JUHAN = 'juhan.viik@gmail.com'
    PRIIT = 'priit.patt@gmail.com'
    TOOMAS = 'toomas.kruus@gmail.com'


class Prefix:
    BOOK = '/book_api'
    USER = '/user_api'


class BookEndpoints:
    FETCH_ALL = f'{Prefix.BOOK}/add_new_book'
    ADD_BOOK = f'{Prefix.BOOK}/add_new_book'
    BOOK_ACTIVITY = f'{Prefix.BOOK}/activity'
    RESERVE_BOOK = f'{Prefix.BOOK}/reserve_book'
    RECEIVE_BOOK = f'{Prefix.BOOK}/receive_book'
    REMOVE_BOOK = f'{Prefix.BOOK}/remove_book'
    CANCEL_RESERVATION = f'{Prefix.BOOK}/cancel_reservation'
    RETURN_BOOK = f'{Prefix.BOOK}/return_book'


class UserEndpoints:
    CHANGE_DURATION = f'{Prefix.USER}/change_duration'
    REGISTER = f'{Prefix.USER}/register'
    LOGIN = f'{Prefix.USER}/login'
    LOGOUT = f'{Prefix.USER}/logout'


class TestBooks:
    cashflow = {
        'title': "Rich Dad's CASHFLOW Quadrant: Rich Dad's Guide to Financial Freedom",
        'author': 'Robert Kiyosaki',
        'imageUrl': 'https://m.media-amazon.com/images/I/71+SWQ6xj1L._SY466_.jpg',
        'description': 'Cashflow description'
    }
    rich_dad = {
        'title': 'Rich Dad Poor Dad',
        'author': 'Robert Kiyosaki',
        'imageUrl': 'https://upload.wikimedia.org/wikipedia/en/thumb/b/b9/Rich_Dad_Poor_Dad.jpg/220px'
                    '-Rich_Dad_Poor_Dad.jpg',
        'description': 'First book'
    }
