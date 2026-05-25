from http import HTTPStatus

from fastapi.testclient import TestClient

from api.app import app
from api.security import create_acess_token


def test_create_user(client):
    client = TestClient(app)
    response = client.post(
        '/users/',
        json={
            'username': 'Mayckon',
            'email': 'mayckonkennedy877@gmail.com',
            'password': 'secret',
        },
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'username': 'Mayckon',
        'email': 'mayckonkennedy877@gmail.com',
        'id': 1,
    }


def test_read_users(client):
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


def test_update_user(client, user, token):
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'Maria Eduarda',
            'email': 'ms.mariasilva@gmail.com',
            'password': 'secretkey',
            'id': 1,
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'Maria Eduarda',
        'email': 'ms.mariasilva@gmail.com',
        'id': user.id,
    }


def test_delete_user(client, user, token):
    response = client.delete(
        f'/users/{user.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}


def test_update_user_not_found(client, user, token):
    response = client.put(
        f'/users/{user.id + 1}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'Eduardo de Carvalho',
            'email': 'dudu@gmail.com',
            'password': '123456',
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_update_user_not_permission(client, token):

    response_post = client.post(
        '/users/',
        json={
            'username': 'outro_usuario',
            'email': 'teste@gmail.com',
            'password': '123',
        },
    )

    outro_usuario = response_post.json()

    response = client.put(
        f'/users/{outro_usuario["id"]}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'Eduardo de Carvalho',
            'email': 'dudu@gmail.com',
            'password': '123456',
        },
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


def test_delete_user_not_found(client, user, token):
    response = client.delete(
        f'/users/{user.id + 1}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}

def test_username_already_exists(client):
    client.post(
        '/users/',
        json={
            'username': 'Usuario Teste',
            'email': 'teste@gmail.com',
            'password': '123456',
        },
    )

    response_exists = client.post(
        '/users/',
        json={
            'username': 'Usuario Teste',
            'email': 'email@gmail.com',
            'password': '123456',
        },
    )

    assert response_exists.status_code == HTTPStatus.CONFLICT
    assert response_exists.json() == {'detail': 'Username already exists'}


def test_email_already_exists(client):
    client.post(
        '/users/',
        json={
            'username': 'Usuário Teste',
            'email': 'teste@123.com',
            'password': '123456',
        },
    )

    response_email_exists = client.post(
        '/users/',
        json={
            'username': 'Jose',
            'email': 'teste@123.com',
            'password': '123456',
        },
    )

    assert response_email_exists.status_code == HTTPStatus.CONFLICT
    assert response_email_exists.json() == {'detail': 'Email already exists'}


def test_update_integrity_error(client, user, token):
    client.post(
        '/users/',
        # headers={'Authorization', f'Bearer {token}'},
        json={
            'username': 'Jõao',
            'email': 'mayckonkennedy877@gmail.com',
            'password': 'testepassword',
        },
    )

    response_update = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'João',
            'email': 'mayckonkennedy877@gmail.com',
            'password': 'mynewpassword',
        },
    )

    assert response_update.status_code == HTTPStatus.CONFLICT
    assert response_update.json() == {'detail': 'Username or Email already exists'}


def test_get_current_user_not_found(client):
    data = {'no-email': 'test'}
    token = create_acess_token(data)

    response = client.delete(
        '/users/1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}
