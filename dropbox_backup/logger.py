import logging


def get_logger(module_name):
    logger = logging.getLogger(module_name)
    stream = logging.StreamHandler()
    logger.addHandler(stream)
    return logger
