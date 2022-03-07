# from sqlalchemy import create_engine
import pdb
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from ...config import ConfigClass
from logger import LoggerFactory

SQLALCHEMY_DATABASE_URL = ConfigClass.RDS_DB_URI

print(ConfigClass.RDS_DB_URI)
engine = create_async_engine(ConfigClass.RDS_DB_URI)
print(engine.url)
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

Base = declarative_base()
_logger = LoggerFactory("Helpers").get_logger()

class SingletonMetaClass(type):
    def __init__(cls,name,bases,dict):
        super(SingletonMetaClass,cls)\
          .__init__(name,bases,dict)
        original_new = cls.__new__
        def my_new(cls,*args,**kwds):
            if cls.instance == None:
                cls.instance = \
                  original_new(cls,*args,**kwds)
            return cls.instance
        cls.instance = None
        cls.__new__ = staticmethod(my_new)

    
class DBConnection:
    __metaclass__ = SingletonMetaClass

    async def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            _logger.debug("Closed db")
            await db.close()

