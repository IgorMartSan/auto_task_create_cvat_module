import os
import logging
from logging.handlers import RotatingFileHandler

def setup_logger(LOG_DIR, CONTAINER_NAME):
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    PATH_LOG = f"{LOG_DIR}/{CONTAINER_NAME}.log"

    logger = logging.getLogger()
    rotating_handler = RotatingFileHandler(PATH_LOG, maxBytes=10 * 1024 * 1024, backupCount=1)
    rotating_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    rotating_handler.setFormatter(rotating_formatter)
    logger.addHandler(rotating_handler)

def get_logger():
    return logging.getLogger()
