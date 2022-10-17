from sqlalchemy import update, delete
from sqlalchemy.future import select

from uuid import uuid4

from database import db, transaction

from models import Todo

from utils.task_scheduler import is_schedule_valid, deschedule_todo


async def fetch_all_todos(user_id: str) -> list:
    query = select(Todo).where(Todo.user_id == user_id)
    data = await db.execute(query)
    data = data.scalars().all()
    if not data:
        return ['No TODOs for this user']
    return data


async def fetch_todo(id: str) -> dict:
    query = select(Todo).where(Todo.id == id)
    todo = await db.execute(query)
    todo = todo.scalar()
    if todo:
        todo = todo.__dict__
        return todo
    return {'TodoNotFoundError': 'No todo was found with this id.'}


async def check_if_todo_title_exists(title: str) -> bool:
    query = select(Todo).where(Todo.title == title)
    todo = await db.execute(query)
    if todo.scalar():
        return True
    return False


async def insert_todo(todo: dict) -> dict:
    # for task scheduling
    new_id = uuid4().hex
    new_todo = Todo(
        id = new_id,
        **todo,
    )

    db.add(new_todo)
    output = await transaction(msg=f'Todo successfully added: {todo}')
    output.update({'todo_id': new_id})
    return output


async def update_todo(id: str, **kwargs) -> dict:
    stmt = (
        update(Todo)
        .where(Todo.id == id)
        .values(**kwargs)
        .execution_options(synchronize_session='fetch')
    )

    await db.execute(stmt)
    return await transaction(msg='Todo succesffuly updated.')


async def do_todo(id: str) -> bool:
    stmt = (
        update(Todo)
        .where(Todo.id == id)
        .values(is_done=True)
        .execution_options(synchronize_session='fetch')
    )

    await db.execute(stmt)
    return await transaction(msg='Todo successfully marked as done.')


async def delete_todo(id: str) -> dict:
    todo = await fetch_todo(id)
    if is_schedule_valid(todo.get('remind_on')):
        await deschedule_todo(id)

    stmt = delete(Todo).where(Todo.id == id).returning(Todo.id, Todo.title)
    affected_row = await db.execute(stmt)
    affected_row = affected_row.first()

    if affected_row:
        return await transaction(f'Todo successully deleted: {affected_row}')
    
    return {'NoTodosFoundError': 'No user was found with this id.'}


async def delete_all_todos(user_id: str) -> dict:
    stmt = delete(Todo).where(Todo.user_id == user_id).returning(Todo.id, Todo.title)
    affected_row = await db.execute(stmt)
    affected_row = affected_row.first()

    if affected_row:
        return await transaction(f'All TODOs successully deleted for the user.')
    
    return {'NoTodosFoundError': 'The user has no TODOs.'}
