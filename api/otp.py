from fastapi import APIRouter, Depends

from config import Config, error_message

from crud.users import add_telegram_id
from crud.otp import (
    fetch_otp_by_user_id,
    insert_otp,
    update_pin,
    authorize_otp,
)

from utils.otp_handler import (
    generate_new_pin,
    send_message,
    create_otp_record,
    is_otp_expired,
)

from utils.auth_handler import get_current_user


otp = APIRouter(prefix=Config.OTP_PREFIX)


@otp.post('/getOTP/', tags=['OTP'])
async def generate_otp(telegram_id: int, user_id: str = Depends(get_current_user)):
    otp_in_database = await fetch_otp_by_user_id(user_id)
    if not otp_in_database.get('NoOTPsFoundError'):
        if otp_in_database.get('authorized'):
            return {'AlreadyAuthorizedError': 'User has already been authorized.'}
        
        new_pin = generate_new_pin()
        telegram_message = f'Your new TodoApp authentication pin code:\n\n{new_pin["new_pin"]}'
        if await update_pin(id=otp_in_database.get('id'), **new_pin):
            if await send_message(otp_in_database.get('telegram_id'), telegram_message):
                return {'Success': 'New OTP successfully generated and sent.'}
        raise error_message[400]
    
    otp_record = create_otp_record(user_id, telegram_id)
    telegram_message = f'Your TodoApp authentication pin code:\n\n{otp_record.get("pin")}'
    if await insert_otp(otp_record):
        if await send_message(telegram_id, telegram_message):
            return {'Success': 'OTP successfully generated and sent.'}
    raise error_message[400]


@otp.put('/redeemOTP/', tags=['OTP'])
async def redeem_otp(pin: int, user_id: str = Depends(get_current_user)):
    otp_in_database = await fetch_otp_by_user_id(user_id)
    if otp_in_database.get('NoOTPsFoundError'):
        return {'OTPError': 'No OTP record exists for the current user.'}
    
    if pin == otp_in_database.get('pin'):
        if is_otp_expired(otp_in_database.get('expiry')):
            return {'OTPError': 'This OTP is expired. You must request a new one.'}
        
        response = await authorize_otp(otp_in_database.get('id'))
        if response:
            if await add_telegram_id(otp_in_database.get('user_id'), otp_in_database.get('telegram_id')):
                return {'Success': 'User successfully authorized.'}
            return {'TelegramWarning': 'User has been authorized, but the confirmation message could not be delivered.'}
        raise error_message[400]
    
    return {'OTPError': 'Wrong OTP pin.'}
