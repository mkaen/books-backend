from test_constants import BookEndpoints


def reserve_and_receive_book(client, book_id):
    try:
        client.patch(f'{BookEndpoints.RESERVE_BOOK}/{book_id}')
        client.patch(f'{BookEndpoints.RECEIVE_BOOK}/{book_id}')
    except Exception as e:
        return e
