from __future__ import annotations
import logging
import os
from pathlib import Path

from .config import log_dir, log_to_console, log_to_file, log_level

log_file_name = f"{log_dir}\\{Path(__file__).parent.name}.log"

logging.basicConfig(level=log_level,
                    format="%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s", )
logger = logging.getLogger("UNFI PRODUCT SEARCH")
# if log_to_console:
#     logger.addHandler(logging.StreamHandler())

if log_to_file:
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    logger.info(f"Logging to file: {log_file_name}")
    file_handler = logging.FileHandler(log_file_name)
    file_handler.setLevel(log_level)


if not log_to_file and not log_to_console:
    # log to null and only null
    logger.addHandler(logging.NullHandler())

    logger.info("Logging to null")


def get_logger(name: str) -> logging.Logger:
    return logger.getChild(name)

