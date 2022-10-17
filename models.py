from sqlalchemy import Column, ForeignKey, Boolean, Integer, Float, String, DateTime
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(String(32), primary_key=True, index=True)
    username = Column(String(24), index=True, nullable=False, unique=True)
    password = Column(String(64), nullable=False)
    name = Column(String(30), nullable=False)
    email = Column(String(64), index=True, unique=True)
    telegram_id = Column(Integer, index= True, unique=True, nullable=True)

    # one-to-many relationship
    todos = relationship('Todo', back_populates='author', cascade='all, delete', passive_deletes=True)
    # uselist is for making it a one-to-one relationship
    otp = relationship('OTP', back_populates='user', cascade='all, delete', uselist=False, passive_deletes=True)


class Todo(Base):
    __tablename__ = 'todos'

    id = Column(String(32), primary_key=True, index=True)
    user_id = Column(String(32), ForeignKey('users.id', ondelete='CASCADE'), index=True)
    title = Column(String(24), unique=True, nullable=False, index=True)
    detail = Column(String(255), nullable=False)
    is_done = Column(Boolean, default=False, nullable=False)
    remind_on = Column(DateTime(timezone=True), nullable=True)

    author = relationship('User', back_populates='todos')


class OTP(Base):
    __tablename__ = 'otp'

    id = Column(String(32), primary_key=True, index=True)
    pin = Column(Integer, nullable=False)
    user_id = Column(String(32), ForeignKey('users.id', ondelete='CASCADE'), index=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    expiry = Column(Float, nullable=False)  # UNIX timestamp
    authorized = Column(Boolean, nullable=False, default=False)

    # for one-to-one relationships, only the parent requires to have `uselist=False` argument
    user = relationship('User', back_populates='otp')
