from http import HTTPStatus

from api.security import create_acess_token


def test_get_token(client, user):
    response = client.post(
        '/auth/token', data={'username': user.email, 'password': user.clean_password}
    )

    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'acess_token' in token
    assert 'token_type' in token


def test_get_current_not_exists(client):
    data = {'sub': 'test@test'}

    token = create_acess_token(data)

    response = client.delete('/users/1', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_login_user_not_exists(client):
    pyload = {'username': 'teste@mayckon.com', 'password': 'secret_key'}

    response = client.post('/auth/token', data=pyload)

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}


def test_login_not_verify_password(client, token):
    client.post(
        '/users',
        headers={'Authorization': f'Bearer {token}'},
        json={'username': 'Duarte', 'email': 'duarte@gmail.com', 'password': '123456'},
    )

    pyload = {'username': 'duarte@gmail.com', 'password': '987654'}

    response = client.post('/auth/token', data=pyload)

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}
