from fastapi import APIRouter, Depends

from config import Config, error_message

from crud.users import fetch_user_by_id

from crud.todos import (
    delete_all_todos,
    fetch_todo,
    fetch_all_todos,
    check_if_todo_title_exists,
    insert_todo,
    update_todo,
    do_todo,
    delete_todo,
)

from schemas import Todo

from utils.auth_handler import get_current_user
from utils.task_scheduler import is_schedule_valid, schedule_todo, reschedule_todo


todos = APIRouter(prefix=f'{Config.USERS_PREFIX}{Config.TODOS_PREFIX}')


@todos.get('/getTodos/', tags=['Todo'])
async def get_todos(user_id: str = Depends(get_current_user)):
    response = await fetch_all_todos(user_id)
    if response:
        return response
    raise error_message[400]


@todos.post('/addTodo/', tags=['Todo'])
async def add_todo(todo: Todo, user_id: str = Depends(get_current_user)):
    todo = todo.dict()
    if await check_if_todo_title_exists(todo.get('title')):
        return {'TitleAlreadyExistsError': 'Another todo with the same title already exists for this user.'}
    
    user_in_database = await fetch_user_by_id(user_id)
    telegram_id = user_in_database.get('telegram_id')

    remind_on = todo.get('remind_on')
    
    if remind_on and not telegram_id:
        return {'UserNotAuthenticatedError': 'User has not yet authenticated their telegram account and cannot set reminders.'}

    if remind_on and not is_schedule_valid(remind_on):
        return {'ScheduleInvalidError': 'The received schedule is invalid. Please enter a valid datetime.'}

    todo.update({'user_id': user_id})

    response = await insert_todo(todo)
    if response:
        if remind_on and telegram_id:
            await schedule_todo(todo, response.get('todo_id'), telegram_id)
            response.update({'schedule success': 'Todo successully scheduled.'})
        return response
    raise error_message[400]


@todos.put('/updateTodo/', tags=['Todo'])
async def edit_todo(todo: Todo = None, user_id: str = Depends(get_current_user), todo_id: str = None):
    todo_in_database = await fetch_todo(todo_id)

    if not user_id == todo_in_database.get('user_id'):
        raise error_message[401]

    todo = {key: value for key, value in todo.dict().items() if value != ''}
    
    response = await update_todo(todo_id, **todo)

    if response:
        # rescheduling the todo
        remind_on = todo.get('remind_on')
        if remind_on:
            user_in_database = await fetch_user_by_id(user_id)
            telegram_id = user_in_database.get('telegram_id')
            if telegram_id:
                todo_in_database.update({**todo})
                await reschedule_todo(todo_in_database, telegram_id=telegram_id)
        return response
    raise error_message[400]


@todos.put('/doTodo/', tags=['Todo'])
async def finish_todo(user_id: str = Depends(get_current_user), todo_id: str = None):
    todo_in_database = await fetch_todo(todo_id)

    if not user_id == todo_in_database.get('user_id'):
        raise error_message[401]
    
    response = await do_todo(todo_id)
    if response:
        return response
    raise error_message[400]


@todos.delete('/deleteTodo/', tags=['Todo'])
async def remove_todo(user_id: str = Depends(get_current_user), todo_id: str = None):
    todo_in_database = await fetch_todo(todo_id)

    if not user_id == todo_in_database.get('user_id'):
        raise error_message[401]

    response = await delete_todo(todo_id)
    if response:
        return response
    raise error_message[400]


@todos.delete('/deleteAllTodos/', tags=['Todo'])
async def remove_all_todos(user_id: str = Depends(get_current_user)):
    response = await delete_all_todos(user_id)
    if response:
        return response
    raise error_message[400]
