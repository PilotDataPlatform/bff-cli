from pythonjsonlogger import jsonlogger
import datetime
import os
import sys
sys.path.append("../..")
from ..namespace import namespace


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record['level'] = record.levelname
        log_record['namespace'] = namespace
        log_record['sub_name'] = record.name

def formatter_factory():
    namespace = os.getcwd().split("/")[-1]
    return CustomJsonFormatter(fmt='%(asctime)s %(namespace)s %(sub_name)s %(level)s %(message)s')

