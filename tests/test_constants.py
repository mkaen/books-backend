class TestUserEmail:
    JUHAN = 'juhan.viik@gmail.com'
    PRIIT = 'priit.patt@gmail.com'
    TOOMAS = 'toomas.kruus@gmail.com'


class Prefix:
    BOOK = '/book_api'
    USER = '/user_api'


class BookEndpoints:
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
