from http import HTTPStatus

from fastapi.testclient import TestClient

from api.app import app
from api.schemas import UserResponseSchema

client = TestClient(app)


def test_create_user(client):
    client = TestClient(app)
    response = client.post(
        '/users',
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


def test_update_user(client, user):
    response = client.put(
        f'/users/{user.id}',
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
        'id': 1,
    }


def test_delete_user(client, user):
    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}


def test_update_user_not_found(client):
    response = client.put(
        '/users/999',
        json={
            'username': 'Eduardo de Carvalho',
            'email': 'dudu@gmail.com',
            'password': '123456',
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_delete_user_not_found(client):
    response = client.delete('/users/999')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_read_users_with_users(client, user):
    user_schema = UserResponseSchema.model_validate(user).model_dump()
    response = client.get('/users/')
    assert response.json() == {'users': [user_schema]}


def test_update_integrity_error(client, user):
    client.post(
        '/users',
        json={
            'username': 'Welliton',
            'email': 'wellitonduarte@gmail.com',
            'password': '123456',
        },
    )

    response_update = client.put(
        f'/users/{user.id}',
        json={
            'username': 'Welliton',
            'email': 'ms.mariasilva@gmail.com',
            'password': 'mypassword_test',
        },
    )

    assert response_update.status_code == HTTPStatus.CONFLICT
    assert response_update.json() == {'detail': 'Username or Email already exists'}


def test_username_already_exists(client):
    client.post(
        '/users',
        json={
            'username': 'Usuario Teste',
            'email': 'teste@gmail.com',
            'password': '123456',
        },
    )

    response_exists = client.post(
        '/users',
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
        '/users',
        json={
            'username': 'Usuário Teste',
            'email': 'teste@123.com',
            'password': '123456',
        },
    )

    response_email_exists = client.post(
        '/users',
        json={
            'username': 'Jose',
            'email': 'teste@123.com',
            'password': '123456',
        },
    )

    assert response_email_exists.status_code == HTTPStatus.CONFLICT
    assert response_email_exists.json() == {'detail': 'Email already exists'}
