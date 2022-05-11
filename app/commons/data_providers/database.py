# Copyright (C) 2022 Indoc Research
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from ...config import ConfigClass

SQLALCHEMY_DATABASE_URL = ConfigClass.RDS_DB_URI

engine = create_async_engine(ConfigClass.RDS_DB_URI)
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

Base = declarative_base()


class SingletonMetaClass(type):

    def __init__(cls, name, bases, _dict):
        super(SingletonMetaClass, cls).__init__(name, bases, _dict)
        original_new = cls.__new__

        def my_new(cls, *args, **kwds):
            if cls.instance is None:
                cls.instance = original_new(cls, *args, **kwds)
            return cls.instance
        cls.instance = None
        cls.__new__ = staticmethod(my_new)


class DBConnection(metaclass=SingletonMetaClass):

    async def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            await db.close()
