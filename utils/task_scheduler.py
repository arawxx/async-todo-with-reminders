from utils.celery_worker import app, celery_schedule_todo

import time
from datetime import datetime


def is_schedule_valid(schedule: datetime) -> bool:
    # first, turn the times into timestamp
    now = time.time()
    schedule = datetime.timestamp(schedule)
    if now > schedule:
        return False
    return True


async def schedule_todo(todo: dict, todo_id: str, telegram_id: int) -> None:
    message = f'<i>TODO reminder</i>\n\n<b>{todo.get("title")}</b>\n{todo.get("detail")}'
    celery_schedule_todo.apply_async(args=(telegram_id, message), eta=todo.get('remind_on'), task_id=todo_id)


async def reschedule_todo(todo: dict, telegram_id: int) -> None:
    app.control.revoke(todo.get('id'), terminated=True, signal='SIGKILL')
    await schedule_todo.apply_async(todo, telegram_id)


async def deschedule_todo(todo_id: str) -> None:
    app.control.revoke(todo_id, terminated=True, signal='SIGKILL')
