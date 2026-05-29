from http import HTTPStatus

import factory
import factory.fuzzy
import pytest

from api.models import Todo, TodoState


class TodoFactory(factory.Factory):  # type: ignore
    class Meta:  # type: ignore
        model = Todo

    title = factory.Faker('text')  # type: ignore
    description = factory.Faker('text')  # type: ignore
    state = factory.fuzzy.FuzzyChoice(TodoState)
    user_id = 1


@pytest.mark.asyncio
async def test_create_todo(client, token):
    response = await client.post(
        '/todos/',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'title': 'Test todo',
            'description': 'Test todo description',
            'state': 'draft',
        },
    )

    assert response.json() == {
        'id': 1,
        'title': 'Test todo',
        'description': 'Test todo description',
        'state': 'draft',
    }


@pytest.mark.asyncio
async def test_list_filter_todos_should_return_5_todos(session, client, user, token):

    expected_todos = 5
    session.add_all(TodoFactory.create_batch(5, user_id=user.id))

    await session.commit()

    response = await client.get('/todos/', headers={'Authorization': f'Bearer {token}'})

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_filter_todos_should_return_2_todos(session, client, user, token):

    expected_todos = 2
    session.add_all(TodoFactory.create_batch(5, user_id=user.id))

    await session.commit()

    response = await client.get('/todos/?offset=0&limit=2', headers={'Authorization': f'Bearer {token}'})
    # breakpoint()

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_filter_title_should_return_5(session, client, user, token):

    expected_todos = 5
    session.add_all(TodoFactory.create_batch(5, user_id=user.id, title='Test todo 1'))
    # session.add_all(TodoFactory.create_batch(5, user_id=user.id))

    await session.commit()

    response = await client.get('/todos/?title=Test todo 1', headers={'Authorization': f'Bearer {token}'})

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_filter_description_should_return_5(session, client, user, token):

    expected_todos = 5
    session.add_all(TodoFactory.create_batch(5, user_id=user.id, description='Description todo 1'))
    # session.add_all(TodoFactory.create_batch(5, user_id=user.id))

    await session.commit()

    response = await client.get('/todos/?description=Description todo 1', headers={'Authorization': f'Bearer {token}'})

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_filter_state_should_return_5(session, client, user, token):

    expected_todos = 5
    session.add_all(TodoFactory.create_batch(5, user_id=user.id, state='draft'))
    # session.add_all(TodoFactory.create_batch(5, user_id=user.id))

    await session.commit()

    response = await client.get('/todos/?state=draft', headers={'Authorization': f'Bearer {token}'})

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_delet_todo(client, session, token, user):
    todo = TodoFactory(user_id=user.id)

    session.add(todo)
    await session.commit()

    response = await client.delete(
        f'/todos/{todo.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Task has been deleted successfully.'}


@pytest.mark.asyncio
async def test_delete_todo_error(client, token):
    response = await client.delete('/todos/200', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found.'}
