import os
import time

from random import randint

from aiogram import Bot, types
from aiogram.utils import exceptions


token = os.getenv('BOT_TOKEN')
bot = Bot(token=token, parse_mode=types.ParseMode.HTML)


async def send_message(user_id: int, text: str, disable_notification: bool = False) -> bool:
    try:
        await bot.send_message(user_id, text, disable_notification=disable_notification)
    except exceptions.BotBlocked:
        print(f'Target [ID:{user_id}]: blocked by user')
    except exceptions.ChatNotFound:
        print(f'Target [ID:{user_id}]: invalid user ID')
    except exceptions.UserDeactivated:
        print(f'Target [ID:{user_id}]: user is deactivated')
    except exceptions.TelegramAPIError:
        print(f'Target [ID:{user_id}]: failed')
    else:
        print(f'Target [ID:{user_id}]: success')
        return True
    return False


def create_otp_record(user_id: str, telegram_id: int) -> dict:
    record = {
        'user_id': user_id,
        'telegram_id': telegram_id,
        'pin': randint(1000, 10000),
        'expiry': (time.time() + 120),
        'authorized': False
    }
    return record


def generate_new_pin() -> dict:
    new_pin = {
        'new_pin': randint(1000, 10000),
        'new_expiry': (time.time() + 120)
    }
    return new_pin


def is_otp_expired(expiry: float) -> bool:
    if time.time() > expiry:
        return True
    return False
