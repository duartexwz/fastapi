from http import HTTPStatus

import factory.fuzzy
import pytest
from factory.alchemy import SQLAlchemyModelFactory
from httpx import (
    AsyncClient,  # Usaremos o cliente assíncrono oficial recomendado para FastAPI
)
from sqlalchemy.future import select

from api.models import Todo, TodoState, User


# 1. Correção da Factory para o ecossistema SQLAlchemy
class TodoFactory(SQLAlchemyModelFactory):
    class Meta:  # type: ignore
        model = Todo
        # Não precisa travar a sessão aqui se usarmos a fixture abaixo

    title = factory.Faker('text')  # type: ignore
    description = factory.Faker('text')  # type: ignore
    state = factory.fuzzy.FuzzyChoice(TodoState)
    user_id = 1


# ==============================================================================
# TESTES DE API (INTEGRAÇÃO)
# ==============================================================================


@pytest.mark.asyncio
async def test_list_todos_should_return_5_todos(
    session, client: AsyncClient, user, token
):
    # Vincula a sessão atual à Factory para este teste
    TodoFactory._meta.sqlalchemy_session = session  # type: ignore
    expected_todos = 5

    # Cria os todos garantindo o ID do usuário correto da fixture
    todos = TodoFactory.create_batch(5, user_id=user.id)
    session.add_all(todos)
    await session.commit()

    # Requisição assíncrona usando await
    response = client.get(
        '/todos/',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK  # type: ignore
    assert len(response.json()['todos']) == expected_todos  # type: ignore


@pytest.mark.asyncio
async def test_list_todos_pagination_should_return_2_todos(
    session, user, client: AsyncClient, token
):
    TodoFactory._meta.sqlalchemy_session = session  # type: ignore
    expected_todos = 2

    session.add_all(TodoFactory.create_batch(5, user_id=user.id))
    await session.commit()

    response = client.get(
        '/todos/?offset=1&limit=2',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK  # type: ignore
    assert len(response.json()['todos']) == expected_todos  # type: ignore


@pytest.mark.asyncio
async def test_list_todos_filter_title_should_return_5_todos(
    session, user, client: AsyncClient, token
):
    TodoFactory._meta.sqlalchemy_session = session  # type: ignore
    expected_todos = 5

    session.add_all(TodoFactory.create_batch(5, user_id=user.id, title='Test todo 1'))
    await session.commit()

    response = client.get(
        '/todos/?title=Test todo 1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK  # type: ignore
    assert len(response.json()['todos']) == expected_todos  # type: ignore


@pytest.mark.asyncio
async def test_list_todos_filter_description_should_return_5_todos(
    session, user, client: AsyncClient, token
):
    TodoFactory._meta.sqlalchemy_session = session  # type: ignore
    expected_todos = 5

    session.add_all(
        TodoFactory.create_batch(5, user_id=user.id, description='description')
    )
    await session.commit()

    response = client.get(
        '/todos/?description=desc',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK  # type: ignore
    assert len(response.json()['todos']) == expected_todos  # type: ignore


@pytest.mark.asyncio
async def test_list_todos_filter_state_should_return_5_todos(
    session, user, client: AsyncClient, token
):
    TodoFactory._meta.sqlalchemy_session = session  # type: ignore
    expected_todos = 5

    session.add_all(TodoFactory.create_batch(5, user_id=user.id, state=TodoState.draft))
    await session.commit()

    response = client.get(
        '/todos/?state=draft',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK  # type: ignore
    assert len(response.json()['todos']) == expected_todos  # type: ignore


@pytest.mark.asyncio
async def test_list_todos_filter_combined_should_return_5_todos(
    session, user, client: AsyncClient, token
):
    TodoFactory._meta.sqlalchemy_session = session  # type: ignore
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

    assert response.status_code == HTTPStatus.OK  # type: ignore
    assert len(response.json()['todos']) == expected_todos  # type: ignore


# ==============================================================================
# TESTES DE BANCO DE DADOS (UNITÁRIOS)
# ==============================================================================


@pytest.mark.asyncio
async def test_create_todo_db(session, user):
    todo = Todo(
        title='Test Todo',
        description='Test Desc',
        state=TodoState.draft,
        user_id=user.id,
    )

    session.add(todo)
    await session.commit()

    result = await session.scalar(select(Todo))

    assert result.title == 'Test Todo'
    assert result.description == 'Test Desc'
    assert result.state == TodoState.draft
    assert result.user_id == user.id


@pytest.mark.asyncio
async def test_user_todo_relationship(session, user: User):
    todo = Todo(
        title='Test Todo',
        description='Test Desc',
        state=TodoState.draft,
        user_id=user.id,
    )

    session.add(todo)
    await session.commit()
    await session.refresh(user)

    assert todo in user.todos
