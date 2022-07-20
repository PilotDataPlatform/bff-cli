from common import LoggerFactory
from ..config import ConfigClass
from aioredis import StrictRedis


logger = LoggerFactory('api_health').get_logger()


async def redis_check():
    try:
        res = await StrictRedis(
            host=ConfigClass.REDIS_HOST,
            port=ConfigClass.REDIS_PORT,
            db=ConfigClass.REDIS_DB,
            password=ConfigClass.REDIS_PASSWORD
        ).ping()
        logger.info(f'Redis health check result: {res}')
        if res:
            return True
    except Exception as e:
        logger.error(f'Redis health check failed: {e}')
        return False
