from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.models import Todo, User
from api.schemas import FilterTodo, Message, TodoList, TodoPublic, TodoSchema
from api.security import get_current_user, get_session

router = APIRouter(prefix='/todos', tags=['todos'])
CurrentUser = Annotated[User, Depends(get_current_user)]
SessionInject = Annotated[AsyncSession, Depends(get_session)]


@router.post('/', response_model=TodoPublic)
async def create_todo(
    todo: TodoSchema,
    user: CurrentUser,
    session: SessionInject,
):
    db_todo = Todo(
        title=todo.title,
        description=todo.description,
        state=todo.state,
        user_id=user.id,
    )

    session.add(db_todo)
    await session.commit()
    await session.refresh(db_todo)

    return db_todo


@router.get('/', response_model=TodoList)
async def read_todos(
    session: SessionInject,
    user: CurrentUser,
    todo_filter: Annotated[FilterTodo, Query()],
):
    query = select(Todo).where(Todo.user_id == user.id)

    if todo_filter.title:
        query.filter(Todo.title.contains(todo_filter.title))

    if todo_filter.description:
        query.filter(Todo.description.contains(todo_filter.description))

    if todo_filter.state:
        query.filter(Todo.state == todo_filter.state)

    todos = await session.scalars(query.limit(todo_filter.limit).offset(todo_filter.offset))

    return {'todos': todos.all()}


@router.delete('/{todo_id}', response_model=Message)
async def delete_todo(session: SessionInject, user: CurrentUser, todo_id: int):

    todo = await session.scalar(select(Todo).where(Todo.user_id == user.id, Todo.id == todo_id))

    if not todo:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Task not found.')

    await session.delete(todo)
    await session.commit()

    return {'message': 'Task has been deleted successfully.'}
