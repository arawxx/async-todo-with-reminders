from sqlalchemy import update, delete
from sqlalchemy.future import select

from uuid import uuid4

from database import db, transaction

from models import User


async def fetch_all_users() -> list:
    query = select(User)
    users = await db.execute(query)
    users = users.scalars().all()
    if not users:
        return ['No users are registered.']
    return users


async def fetch_user_by_username(username: str) -> dict:
    query = select(User).where(User.username == username)
    user = await db.execute(query)
    user = user.scalar()
    if user:
        user = user.__dict__
        return user
    return {'NoUsersFoundError': 'No user was found with this username.'}


async def fetch_user_by_id(id: str) -> dict:
    query = select(User).where(User.id == id)
    user = await db.execute(query)
    user = user.scalar()
    if user:
        user = user.__dict__
        return user
    return {'NoUsersFoundError': 'No user was found with this id.'}


async def check_if_username_exists(username: str) -> bool:
    # exactly like above fetch_user_by_username method, but returns True or False instead of the whole user
    query = select(User).where(User.username == username)
    user = await db.execute(query)
    if user.scalar():
        return True
    return False


async def check_if_email_exists(email: str) -> bool:
    query = select(User).where(User.email == email)
    user = await db.execute(query)
    if user.scalar():
        return True
    return False


async def insert_user(user: dict) -> dict:
    new_user = User(
        id = uuid4().hex,
        **user,
    )

    # unlike execute, db add is not async, and needs to be commited
    db.add(new_user)
    user.pop('password')
    return await transaction(msg=f'User successfully registered: {user}')


async def update_password(id: str, new_password: str) -> dict:
    stmt = (
        update(User)
        .where(User.id == id)
        .values(password=new_password)
        .execution_options(synchronize_session='fetch')
    )

    await db.execute(stmt)
    return await transaction(msg='Password succesfully changed.')


async def update_user(id: str, **kwargs) -> dict:
    stmt = (
        update(User)
        .where(User.id == id)
        .values(**kwargs)
        .execution_options(synchronize_session='fetch')
    )

    await db.execute(stmt)
    return await transaction(msg='User succesffuly updated.')


async def add_telegram_id(user_id: str, telegram_id: str) -> dict:
    stmt = (
        update(User)
        .where(User.id == user_id)
        .values(telegram_id = telegram_id)
        .execution_options(synchronize_session='fetch')
    )

    await db.execute(stmt)
    return await transaction(msg='Telegram id successfully added.')


async def delete_user(id: str) -> dict:
    stmt = delete(User).where(User.id == id).returning(User.id, User.username)
    affected_row = await db.execute(stmt)
    affected_row = affected_row.first()

    if affected_row:
        return await transaction(f'User successully deleted: {affected_row}')
    
    return {'NoUsersFoundError': 'No user was found with this id.'}


async def delete_all_users() -> dict:
    stmt = delete(User).returning(User.id, User.username)
    affected_row = await db.execute(stmt)
    affected_row = affected_row.first()

    if affected_row:
        return await transaction(f'All users successully deleted.')
    
    return {'NoUsersFoundError': 'No user has been registered yet.'}
