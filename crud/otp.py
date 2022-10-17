from sqlalchemy import update, delete
from sqlalchemy.future import select

from uuid import uuid4

from database import db, transaction

from models import OTP


async def fetch_otp_by_user_id(user_id: str) -> dict:
    query = select(OTP).where(OTP.user_id == user_id)
    otp = await db.execute(query)
    otp = otp.scalar()
    if otp:
        otp = otp.__dict__
        return otp
    return {'NoOTPsFoundError': 'No OTP was found for user with this id.'}


async def insert_otp(otp: dict) -> bool:
    new_otp = OTP(
        id = uuid4().hex,
        **otp,
    )

    db.add(new_otp)
    return await transaction (msg=f'OTP was successfully added: {otp}')


async def update_pin(id: str, new_pin: int, new_expiry: float) -> dict:
    stmt = (
        update(OTP)
        .where(OTP.id == id)
        .values(pin=new_pin, expiry=new_expiry)
        .execution_options(synchronize='fetch')
    )

    await db.execute(stmt)
    return await transaction(msg='OTP successfully updated.')


async def authorize_otp(id: str) -> bool:
    stmt = (
        update(OTP)
        .where(OTP.id == id)
        .values(authorized=True)
        .execution_options(synchronize='fetch')
    )

    await db.execute(stmt)
    return await transaction(msg='User successfully authorized with OTP.')
