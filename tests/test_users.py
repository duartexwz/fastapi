from http import HTTPStatus

import pytest

from api.security import create_access_token


@pytest.mark.asyncio
async def test_create_user(client):
    response = await client.post(
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


@pytest.mark.asyncio
async def test_read_users(client):
    response = await client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


@pytest.mark.asyncio
async def test_update_user(client, user, token):
    response = await client.put(
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


@pytest.mark.asyncio
async def test_delete_user(client, user, token):
    response = await client.delete(f'/users/{user.id}', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}


@pytest.mark.asyncio
async def test_update_user_not_found(client, user, token):
    response = await client.put(
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


@pytest.mark.asyncio
async def test_update_user_not_permission(client, token):

    response_post = await client.post(
        '/users/',
        json={
            'username': 'outro_usuario',
            'email': 'teste@gmail.com',
            'password': '123',
        },
    )

    outro_usuario = response_post.json()

    response = await client.put(
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


@pytest.mark.asyncio
async def test_delete_user_not_found(client, user, token):
    response = await client.delete(
        f'/users/{user.id + 1}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


@pytest.mark.asyncio
async def test_username_already_exists(client):
    await client.post(
        '/users/',
        json={
            'username': 'Usuario Teste',
            'email': 'teste@gmail.com',
            'password': '123456',
        },
    )

    response_exists = await client.post(
        '/users/',
        json={
            'username': 'Usuario Teste',
            'email': 'email@gmail.com',
            'password': '123456',
        },
    )

    assert response_exists.status_code == HTTPStatus.CONFLICT
    assert response_exists.json() == {'detail': 'Username already exists'}


@pytest.mark.asyncio
async def test_email_already_exists(client):
    await client.post(
        '/users/',
        json={
            'username': 'Usuário Teste',
            'email': 'teste@123.com',
            'password': '123456',
        },
    )

    response_email_exists = await client.post(
        '/users/',
        json={
            'username': 'Jose',
            'email': 'teste@123.com',
            'password': '123456',
        },
    )

    assert response_email_exists.status_code == HTTPStatus.CONFLICT
    assert response_email_exists.json() == {'detail': 'Email already exists'}


@pytest.mark.asyncio
async def test_update_integrity_error(client, user, token):
    await client.post(
        '/users/',
        # headers={'Authorization', f'Bearer {token}'},
        json={
            'username': 'Jõao',
            'email': 'mayckonkennedy877@gmail.com',
            'password': 'testepassword',
        },
    )

    response_update = await client.put(
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


@pytest.mark.asyncio
async def test_get_current_user_not_found(client):
    data = {'no-email': 'test'}
    token = create_access_token(data)

    response = await client.delete(
        '/users/1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


@pytest.mark.asyncio
async def test_update_user_with_wrong_user(client, other_user, token):
    response = await client.put(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'TesteUser',
            'email': 'teste@user.com',
            'password': '123456',
        },
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


@pytest.mark.asyncio
async def test_delete_wrong_user(client, other_user, token):
    response = await client.delete(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}
