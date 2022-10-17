from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional


class Todo(BaseModel):
    title: str
    detail: Optional[str] = None
    is_done: bool = False
    remind_on: datetime = None

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str
    email: EmailStr
    name: str


class User(UserBase):
    telegram_id: Optional[int] = None

    class Config:
        orm_mode = True


class UserSignup(UserBase):
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserEdit(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    name: Optional[str] = None


class OTP(BaseModel):
    telegram_id: int
    pin: int
    expiry: float  # UNIX timestamp
    authorized: bool = False
