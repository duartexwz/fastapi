from pydantic import BaseModel, ConfigDict, EmailStr


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
