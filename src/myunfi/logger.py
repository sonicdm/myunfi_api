import logging
import os
import sys
from myunfi.config import logging_enabled, log_level, log_to_console, console_log_level

base_logger = logging.getLogger('myunfi')
base_logger.setLevel(log_level)
base_log_format = logging.Formatter('[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
                                    '%m-%d %H:%M:%S')

if log_to_console:
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_log_level)
    console_handler.setFormatter(base_log_format)
    base_logger.addHandler(console_handler)

if logging_enabled:
    log_file_name = os.path.join(os.path.dirname(__file__), 'myunfi.log')
    file_handler = logging.FileHandler(log_file_name)
    file_handler.setFormatter(base_log_format)
    base_logger.addHandler(file_handler)

if not base_logger.handlers:
    base_logger.addHandler(logging.NullHandler())


def get_logger(name):
    return base_logger.getChild(name)
