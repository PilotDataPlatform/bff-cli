from pythonjsonlogger import jsonlogger
from .namespace_declare import service_namespace
import datetime

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record['level'] = record.levelname
        log_record['namespace'] = service_namespace
        log_record['sub_name'] = record.name

def formatter_factory():
    return CustomJsonFormatter(fmt='%(asctime)s %(namespace)s %(sub_name)s %(level)s %(message)s')