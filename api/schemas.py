from pydantic import BaseModel, ConfigDict, EmailStr, Field

from api.models import TodoState


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserResponseSchema(BaseModel):
    username: str
    email: EmailStr
    id: int
    model_config = ConfigDict(from_attributes=True)


class UserDB(UserSchema):
    id: int


class UserList(BaseModel):
    users: list[UserResponseSchema]


class Token(BaseModel):
    access_token: str
    token_type: str


class FilterPage(BaseModel):
    offset: int = 0
    limit: int = 10


class TodoSchema(BaseModel):
    title: str
    description: str
    state: TodoState = Field(default=TodoState.todo)


class TodoPublic(TodoSchema):
    id: int


class FilterTodo(FilterPage):
    title: str | None = Field(default=None, min_length=3, max_length=30)
    description: str | None = None
    state: TodoState | None = None


class TodoList(BaseModel):
    todos: list[TodoPublic]


class Message(BaseModel):
    message: str


class TodoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    state: TodoState | None = None
