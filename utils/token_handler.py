import os
import time

from fastapi import HTTPException

from jose import jwt, JWTError\


secret_key = os.getenv('SECRET_KEY')
algorithm = os.getenv('ALGORITHM')
expiry_time = float(os.getenv('TOKEN_EXPIRATION_IN_SECONDS'))


def create_token(payload: dict, expiry_time: float = expiry_time) -> str:
    expiry_date = time.time() + expiry_time
    payload.update({'expiry_date': expiry_date})
    encoded_jwt = jwt.encode(payload, secret_key, algorithm=algorithm)
    return encoded_jwt


def decode_token(jwt_token: str) -> dict:
    credentials_exception = HTTPException(
        status_code=401,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'}
    )
    try:
        decoded_token = jwt.decode(jwt_token, secret_key, algorithms=[algorithm])
        if decoded_token['expiry_date'] >= time.time():
            return decoded_token
        raise credentials_exception
    except JWTError:
        raise credentials_exception
