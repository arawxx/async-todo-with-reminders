from fastapi import APIRouter, Depends

from config import Config, error_message

from crud.users import (
    delete_all_users,
    fetch_user_by_id,
    fetch_user_by_username,
    fetch_all_users,
    update_password,
    update_user,
    delete_user,
)

from schemas import UserEdit

from utils.password_handler import hash_password, verify_password
from utils.auth_handler import get_current_user


users = APIRouter(prefix=Config.USERS_PREFIX)


@users.get('/get/', tags=['User'])
async def get_user_by_username(username: str):
    response = await fetch_user_by_username(username)
    if response:
        return response
    raise error_message[400]


@users.get('/getAll/', tags=['User'])
async def get_all_users():
    response = await fetch_all_users()
    if response:
        return response
    raise error_message[400]


@users.put('/updatePassword/', tags=['User'])
async def edit_password(id: str = Depends(get_current_user), old_password: str = None, new_password: str = None):
    if not old_password or not new_password:
        return {'EmptyFieldsError': 'You must fill both the new password field and the old password field!'}
    
    user = await fetch_user_by_id(id)
    password_in_database = user.get('password')
    if not verify_password(old_password, password_in_database):
        return {'PasswordError': 'Current password is incorrect!'}
    
    if old_password == new_password:
        return {'PasswordError': 'The new password entered is same as the current password. Enter a new one.'}
    
    new_password = hash_password(new_password)
    response = await update_password(id, new_password)
    if response:
        return response
    raise error_message[400]


@users.put('/updateUser/', tags=['User'])
async def edit_user(user: UserEdit, id: str = Depends(get_current_user)):
    user = {key: value for key, value in user.dict().items() if value != '' and value != None}
    response = await update_user(id, **user)
    if response:
        return response
    raise error_message[400]


@users.delete('/deleteUser/', tags=['User'])
async def remove_user(id: str = Depends(get_current_user)):
    response = await delete_user(id)
    if response:
        return response
    raise error_message[400]


@users.delete('/deleteAllUsers/', tags=['User'])
async def remove_all_users():
    response = await delete_all_users()
    if response:
        return response
    raise error_message[400]
