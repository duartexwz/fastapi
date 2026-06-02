from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_session
from api.models import User
from api.schemas import (
    FilterPage,
    UserList,
    UserResponseSchema,
    UserSchema,
)
from api.security import get_current_user, get_password_hash

router = APIRouter(prefix='/users', tags=['users'])
T_Session = Annotated[AsyncSession, Depends(get_session)]
T_CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserResponseSchema)
async def create_user(user: UserSchema, session: T_Session):
    db_user = await session.scalar(select(User).where((User.username == user.username) | (User.email == user.email)))
    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Username already exists',
            )
        elif db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Email already exists',
            )

    hashed_password = get_password_hash(user.password)

    db_user = User(username=user.username, password=hashed_password, email=user.email)

    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return db_user


@router.get('/', response_model=UserList)
async def read_users(session: T_Session, filter_users: Annotated[FilterPage, Query()]):

    query = await session.scalars(select(User).offset(filter_users.offset).limit(filter_users.limit))
    users = query.all()

    return {'users': users}


@router.put('/{user_id}', response_model=UserResponseSchema)
async def update_user(
    user_id: int,
    user: UserSchema,
    session: T_Session,
    current_user: T_CurrentUser,
):
    db_user = await session.scalar(select(User).where(User.id == user_id))

    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='User not found',
        )
    if current_user.id != user_id:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions')

    try:
        db_user.username = user.username
        db_user.email = user.email
        db_user.password = get_password_hash(user.password)
        await session.commit()
        await session.refresh(db_user)

    except IntegrityError:
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail='Username or Email already exists')

    return current_user


@router.delete('/{user_id}', status_code=HTTPStatus.OK)
async def delete_user(
    user_id: int,
    session: T_Session,
    current_user: T_CurrentUser,
):

    if current_user.id != user_id:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions')
    await session.delete(current_user)
    await session.commit()

    return {'message': 'User deleted'}
