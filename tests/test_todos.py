import factory
import pytest
from factory.fuzzy import FuzzyChoice

from api.models import Todo, TodoState


def test_create_todo(client, token):
    response = client.post(
        '/todos/',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'title': 'Test Todo',
            'description': 'Test Desc',
            'state': 'draft',
        },
    )

    assert response.json() == {
        'id': 1,
        'title': 'Test Todo',
        'description': 'Test Desc',
        'state': 'draft',
    }


class TodoFactory(factory.Factory):  # type: ignore
    class Meta:  # type: ignore
        model = Todo

    title = factory.Faker('text')  # type: ignore
    description = factory.Faker('text')  # type: ignore
    state = FuzzyChoice(TodoState)
    user_id = 1


@pytest.mark.asyncio
async def test_list_todos_should_return_5_todos(session, client, user, token):
    expected_todos = 5
    session.add_all(TodoFactory.create_batch(5, user_id=user.id))

    await session.commit()

    response = client.get('/todos/', headers={'Authorization': f'Bearer {token}'})

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_should_return_2_todos(client, session, user, token):
    expected_todos = 2
    session.add_all(TodoFactory.create_batch(2, user_id=user.id))

    await session.commit()

    response = client.get(
        '/todos/?offset=1&limit-2', headers={'Authorization': f'Bearer {token}'}
    )

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_filter_title_should_return_5_todos(
    session, client, user, token
):
    expected_todos = 5
    session.add_all(TodoFactory.create_batch(5, user_id=user.id, title='Test todo 1'))

    await session.commit()

    response = client.get(
        '/todos/?title=Test todo 1', headers={'Authorization': f'Bearer {token}'}
    )

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_filter_description_should_return_5_todos(
    session, client, user, token
):
    expected_todos = 5
    session.add_all(
        TodoFactory.create_batch(5, user_id=user.id, description='description')
    )

    await session.commit()

    response = client.get(
        '/todos/?description=desc', headers={'Authorization': f'Bearer {token}'}
    )

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_filter_state_should_return_5_todos(
    session, client, user, token
):
    expected_todos = 5
    session.add_all(TodoFactory.create_batch(5, user_id=user.id, state=TodoState.draft))

    await session.commit()

    response = client.get(
        '/todos/?state=draft', headers={'Authorization': f'Bearer {token}'}
    )

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_filter_combined_should_retuyrn_5_todos(
    session, client, user, token
):
    expected_todos = 5
    session.add_all(
        TodoFactory.create_batch(
            5,
            user_id=user.id,
            title='Test todo combined',
            description='combined description',
            state=TodoState.done,
        )
    )

    session.add_all(
        TodoFactory.create_batch(
            3,
            user_id=user.id,
            title='Other title',
            description='other description',
            state=TodoState.todo,
        )
    )

    await session.commit()

    response = client.get(
        '/todos/?title=Test todo combined&description=combined&state=done',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos
