from fastapi import HTTPException


error_message = {
    400: HTTPException(
        status_code=400,
        detail='Something went wrong / Bad request'
    ),
    401: HTTPException(
        status_code=401,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'}
    )
}


class Config:
    API_PREFIX = '/api/v2'
    
    AUTH_PREFIX = '/auth'
    USERS_PREFIX = '/users'
    TODOS_PREFIX = '/todos'
    OTP_PREFIX = '/otp'