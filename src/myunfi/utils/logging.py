import logging
from pathlib import Path
from typing import Union
from unfi_api.config import UnfiApiConfig as config


def get_logger(name, level=logging.INFO, path=None):
    """
    Returns a logger with the given name and level.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if path:
        set_log_path(logger, path)
    return logger

def init_logger(name: str, level=logging.INFO, log_path: Union[str, Path] = None, console=False):
    """
    Initializes the logger with the given name and level.
    """
    logger = get_logger(name, level)
    if log_path:
        set_log_path(logger, log_path)
    if console:
        ch = logging.StreamHandler()
        ch.setLevel(logger.level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    return logger

def set_logger_level(logger: logging.Logger, level: Union[str, int]):
    """
    Sets the logger level.
    """
    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level)
        
def set_log_path(logger: logging.Logger, path: Union[str, Path]):
    """
    Sets the log path.
    """
    if isinstance(path, str):
        path = Path(path)
    if not path.exists():
        path.mkdir(parents=True)
    fh = logging.FileHandler(path / f'{logger.name}.log')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

def set_global_log_path(path: Union[str, Path]):
    """
    Sets the log path for all loggers
    """
    for logger in logging.Logger.manager.loggerDict.values():
        set_log_path(logger, path)

def set_global_log_level(level: Union[str, int]):
    """
    Sets the log level.
    """
    for logger in logging.Logger.manager.loggerDict.values():
        set_logger_level(logger, level)