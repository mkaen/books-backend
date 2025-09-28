from test_constants import UserEndpoints


def login(client, email, password='123456'):
    """Log in the user."""
    try:
        response = client.post(UserEndpoints.LOGIN, json={
            'email': email,
            'password': password
        })
        return response
    except Exception as e:
        return e


def logout(client):
    """Log out the user."""
    response = client.post(UserEndpoints.LOGOUT)
    return response
