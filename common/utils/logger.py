import logging
import sys

LOG_FORMAT = ('%(levelname) -1s %(asctime)s %(name) -1s %(funcName) '
              '-1s %(lineno) -5d: %(message)s')


def get_logger(name: str) -> logging.Logger:
    """
    To use this, do logger = get_module_logger(__name__)
    """
    logger = logging.getLogger(name)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(LOG_FORMAT)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger
