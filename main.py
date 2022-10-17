from fastapi import FastAPI

from api.auth import auth
from api.users import users
from api.todos import todos
from api.otp import otp

from config import Config

from database import db


app = FastAPI(
    title='Todo App Neo',
    description='A todo app with reminders, using postgresql, sqlalchemy, alembic, arq (Async Redis Queue) and aiogram (Async IO Telegram).',
    version='2.0',
)


@app.on_event('startup')
async def startup():
    await db.create_all()


@app.on_event('shutdown')
async def shutdown():
    await db.close()


@app.get('/', tags=['Homepage'])
async def homepage():
    return {'Message': 'Welcome to the homepage!'}


app.include_router(auth, prefix=Config.API_PREFIX)
app.include_router(users, prefix=Config.API_PREFIX)
app.include_router(todos, prefix=Config.API_PREFIX)
app.include_router(otp, prefix=Config.API_PREFIX)
