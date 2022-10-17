import os

import asyncio

from celery import Celery

from utils.otp_handler import send_message


app = Celery(
    __name__,
    broker= os.getenv('BROKER_URL'),
    backend=os.getenv('BACKEND_URL'),
)


@app.task(bind=True)  # bind=True to be able to access `self` keyword (I left this for my own reference, no uses in this case)
def celery_schedule_todo(self, telegram_id: int, message: str):
    asyncio.run(send_message(telegram_id, message))
