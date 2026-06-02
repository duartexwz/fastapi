from fastapi import FastAPI

from api.routers import auth, todo, users

app = FastAPI()

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(todo.router)
