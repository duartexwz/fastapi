import asyncio
import sys

from fastapi import FastAPI

from api.routers import auth, todo, users

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


app = FastAPI(title='Primeira API com FASTAPI', version='0.1.0')

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(todo.router)
