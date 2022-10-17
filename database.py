import os

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from config import Config
'''from sqlalchemy_utils import database_exists, create_database'''


# get the database url from config file
DB_URL = os.getenv('DB_URL')


# create the database if it does not exist
'''if not database_exists(DB_URL):
    print('Specified database does not exists. Creating it now.')
    create_database(DB_URL)
    print('Database successfully created.')'''


# initialize the database, its Base *class*, and its SessionLocal *class*
Base = declarative_base()


# a boiler-plate transaction function, used in every crud operations after inserting/updating/deleting records
async def transaction(msg: str | None):
    try:
        await db.commit()
        return {'TransactionSuccess': msg}
    except Exception:
        await db.rollback()
        return {'TransactionError': 'Something went wrong / Reverting changes'}


# async database session creator/handler
class AsyncDatabaseSession:
    def __init__(self):
        self.engine = create_async_engine(
            DB_URL,
            future=True,
            echo=False,  # turned off logging; if you can't identify a problem, set this to True
        )
        self.session = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )()

    def __getattr__(self, name):
        return getattr(self.session, name)

    async def create_all(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


db = AsyncDatabaseSession()
