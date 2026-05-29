from contextlib import contextmanager
from datetime import datetime

import factory
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from api.app import app
from api.database import get_session
from api.models import User, table_registry
from api.security import get_password_hash


class UserFactory(factory.Factory):  # type: ignore
    class Meta:  # type: ignore
        model = User

    username = factory.Sequence(lambda n: f'test{n}')  # type: ignore
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@test.com')  # type: ignore
    password = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')  # type: ignore


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine(
        'sqlite+aiosqlite:///:memory:', connect_args={'check_same_thread': False}, poolclass=StaticPool, echo=True
    )

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@pytest_asyncio.fixture
async def client(session):
    async def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as ac:
        yield ac

    app.dependency_overrides.clear()
    # with TestClient(app) as client:
    #     app.dependency_overrides[get_session] = get_session_override
    #     yield client
    # app.dependency_overrides.clear()


@contextmanager
def _mock_db_time(*, model, time=datetime(2026, 1, 1)):
    def fake_time_hook(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time
        if hasattr(target, 'update_at'):
            target.update_at = time

    event.listen(model, 'before_insert', fake_time_hook)

    yield time

    event.remove(model, 'before_insert', fake_time_hook)


@pytest.fixture
def mock_db_time():
    return _mock_db_time


@pytest_asyncio.fixture
async def user(session):
    password = 'testtest'
    user = UserFactory(
        password=get_password_hash(password),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.clean_password = password  # pyright: ignore[reportAttributeAccessIssue]

    return user


@pytest_asyncio.fixture
async def other_user(session):
    password = 'testtest'
    user = UserFactory(password=get_password_hash(password))

    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.clean_password = password

    return user


@pytest_asyncio.fixture
async def token(client, user):
    response = await client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )
    return response.json()['access_token']
