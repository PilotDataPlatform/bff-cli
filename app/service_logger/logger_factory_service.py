import logging
import os, os.path
import sys
from .formatter import formatter_factory
from logging.handlers import TimedRotatingFileHandler


class SrvLoggerFactory:
    def __init__(self, name):
        self.my_formatter = formatter_factory()
        if not os.path.exists("./logs/"):
            os.makedirs("./logs/")
        self.name = name

    def get_logger(self):
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.DEBUG)
        if not logger.handlers:
            # File Handler
            handler = TimedRotatingFileHandler("logs/{}.log".format(self.name),
                                               when='D',
                                               interval=1,
                                               backupCount=2)
            handler.setFormatter(self.my_formatter)
            handler.setLevel(logging.DEBUG)
            # Standard Out Handler
            stdout_handler = logging.StreamHandler(sys.stdout)
            stdout_handler.setFormatter(self.my_formatter)
            stdout_handler.setLevel(logging.DEBUG)
            # Standard Err Handler
            stderr_handler = logging.StreamHandler(sys.stderr)
            stderr_handler.setFormatter(self.my_formatter)
            stderr_handler.setLevel(logging.ERROR)
            # register handlers
            logger.addHandler(handler)
            logger.addHandler(stdout_handler)
            logger.addHandler(stderr_handler)
        return logger
