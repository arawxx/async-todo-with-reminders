import os

from config import Config

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from schemas import UserLogin

from jose import jwt, JWTError

from crud.users import fetch_user_by_username, fetch_user_by_id

from .password_handler import verify_password


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f'{Config.API_PREFIX}{Config.AUTH_PREFIX}/login/')
secret_key = os.getenv('SECRET_KEY')
algorithm = os.getenv('ALGORITHM')


async def authenticate_user(username: str, password: str, from_bot: bool = False):
    credentials_exception = HTTPException(
        status_code=401,
        detail='Incorrect username or password!'
    )

    user_in_database = await fetch_user_by_username(username)
    if user_in_database.get('NoUsersFoundError'):
        if from_bot:
            return False
        raise credentials_exception

    user_in_database = UserLogin(**user_in_database)
    if not verify_password(password, user_in_database.password):
        if from_bot:
            return False
        raise credentials_exception
    return True


# check if the id in the token belongs to the same user in the URL
async def check_username_and_token_id(username: str, id: str):
    credentials_exception = HTTPException(
        status_code=401,
        detail='Incorrect username or password!'
    )

    user_in_database = await fetch_user_by_id(id)
    if not user_in_database:
        raise credentials_exception
    if username == user_in_database.get('username'):
        return True
    return False


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'}
    )

    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        id: str = payload.get('sub')  # same as ['sub'], with a default value for when the key's not there
        if id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await fetch_user_by_id(id)
    if user.get('NoUsersFoundError'):
        raise credentials_exception
    return user['id']
