from dataclasses import asdict

import pytest
from sqlalchemy import select

from api.models import Todo, User


@pytest.mark.asyncio
async def test_model_create_user(session, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(username='Maria Eduarda', email='ms.mariasilva@gmail.com', password='123456')

        session.add(new_user)
        await session.commit()

    user = await session.scalar(select(User).where(User.username == 'Maria Eduarda'))

    assert asdict(user) == {
        'id': 1,
        'username': 'Maria Eduarda',
        'email': 'ms.mariasilva@gmail.com',
        'password': '123456',
        'created_at': time,
        'update_at': time,
        'todos': [],
    }


@pytest.mark.asyncio
async def test_create_todo(session, user):
    todo = Todo(
        title='Teste Todo',
        description='Test Desc',
        state='todo',  # type: ignore
        user_id=user.id,
    )

    session.add(todo)
    await session.commit()

    todo = await session.scalar(select(Todo))

    assert asdict(todo) == {
        'title': 'Teste Todo',
        'id': 1,
        'description': 'Test Desc',
        'state': 'todo',  # type: ignore
        'user_id': 1,
    }
