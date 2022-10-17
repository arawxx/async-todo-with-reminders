from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from config import Config, error_message

from crud.users import (
    insert_user,
    fetch_user_by_username,
    check_if_username_exists,
    check_if_email_exists,
)

from schemas import UserSignup

from utils.password_handler import hash_password
from utils.token_handler import create_token
from utils.auth_handler import authenticate_user


auth = APIRouter(prefix=Config.AUTH_PREFIX)


@auth.post('/signup/', tags=['Authentication'])
async def user_signup(user: UserSignup):
    if await check_if_username_exists(user.username):
        return {'UsernameError': 'This username is already taken / Pick another one'}
    if await check_if_email_exists(user.email):
        return {'EmailError': 'This email has already signed up / Use another one'}

    user.password = hash_password(user.password)
    user = user.dict()
    user.update({'telegram_id': None})
    response = await insert_user(user)
    if response:
        return response
    raise error_message[400]


@auth.post('/login/', tags=['Authentication'])
async def user_login(form: OAuth2PasswordRequestForm = Depends()):
    if await authenticate_user(form.username, form.password):
        user = await fetch_user_by_username(form.username)
        id = user.get('id')
        payload = {'sub': id}
        return {'access_token': create_token(payload), 'token_type': 'Bearer'}
    raise error_message[401]
