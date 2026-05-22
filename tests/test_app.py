from http import HTTPStatus

from fastapi.testclient import TestClient

from api.app import app

client = TestClient(app)


def test_read_main():
    response = client.get('/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'Hello': 'World'}


def test_create_user():
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


def test_read_root():
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'users': [
            {
                'username': 'Mayckon',
                'email': 'mayckonkennedy877@gmail.com',
                'id': 1,
            }
        ]
    }


def test_update_user():
    response = client.put(
        '/users/1',
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


def test_delete_user():
    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


def test_updade_user_not_found():
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


def test_delete_user_not_found():
    response = client.delete('/users/999')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}
