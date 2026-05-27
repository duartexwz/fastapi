from pydantic import BaseModel, ConfigDict, EmailStr

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
    limit: int = 0


class TodoSchema(BaseModel):
    title: str
    description: str
    state: TodoState


class TodoResponseModel(TodoSchema):
    id: int


class TodoList(BaseModel):
    todos: list[TodoResponseModel]


class FilterTodo(FilterPage):
    title: str | None = None
    description: str | None = None
    state: TodoState | None = None


class TodoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    state: TodoState | None = None
