from http import HTTPStatus

import pytest
from freezegun import freeze_time

from api.security import create_access_token


@pytest.mark.asyncio
async def test_get_token(client, user):
    response = await client.post('/auth/token', data={'username': user.email, 'password': user.clean_password})

    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in token
    assert 'token_type' in token


@pytest.mark.asyncio
async def test_get_current_not_exists(client):
    data = {'sub': 'test@test'}

    token = create_access_token(data)

    response = await client.delete('/users/1', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


@pytest.mark.asyncio
async def test_login_user_not_exists(client):
    pyload = {'username': 'teste@mayckon.com', 'password': 'secret_key'}

    response = await client.post('/auth/token', data=pyload)

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}


@pytest.mark.asyncio
async def test_login_not_verify_password(client, token):
    await client.post(
        '/users',
        headers={'Authorization': f'Bearer {token}'},
        json={'username': 'Duarte', 'email': 'duarte@gmail.com', 'password': '123456'},
    )

    pyload = {'username': 'duarte@gmail.com', 'password': '987654'}

    response = await client.post('/auth/token', data=pyload)

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}


@pytest.mark.asyncio
async def test_token_expiret_after_time(client, user):
    with freeze_time('2026-05-26 11:10'):
        response = await client.post(
            '/auth/token',
            data={'username': user.email, 'password': user.clean_password},
        )

        assert response.status_code == HTTPStatus.OK
        token = response.json() == ['access_token']

    with freeze_time('2026-05-26 11:31'):
        response = await client.put(
            f'/users/{user.id}',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'username': 'wrongwrong',
                'email': 'wrong@email.com',
                'password': 'wrongTeste',
            },
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Could not validate credentials'}


@pytest.mark.asyncio
async def test_token_inexistent_user(client):
    response = await client.post('/auth/token', data={'username': 'no@user.com', 'password': 'testtest'})

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}


@pytest.mark.asyncio
async def test_token_wrong_password(client, user):
    response = await client.post('/auth/token', data={'username': user.email, 'password': 'wrong_password'})
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}


@pytest.mark.asyncio
async def test_refresh_token(client, token):
    response = await client.post(
        '/auth/refresh_token',
        headers={'Authorization': f'Bearer {token}'},
    )

    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in data
    assert 'token_type' in data
    assert data['token_type'] == 'bearer'


@pytest.mark.asyncio
async def test_token_expired_dont_refresh(client, user):
    with freeze_time('2023-07-14 12:00:00'):
        response = await client.post(
            '/auth/token',
            data={'username': user.email, 'password': user.clean_password},
        )
        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time('2023-07-14 12:31:00'):
        response = await client.post(
            '/auth/refresh_token',
            headers={'Authorization': f'Bearer {token}'},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Could not validate credentials'}
