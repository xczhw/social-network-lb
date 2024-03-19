import logging
import time

from utils import *

# 创建一个logger
def get_logger(path, filename):
    create_if_not_exists(path)
    filepath = f"{path}/{filename}"
    logger = logging.getLogger(filepath)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(filepath)
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

# 写入系统信息
def log_sys_info():
    logger = get_logger(LOGPATH, 'log.txt')
    while True:
        info = get_sys_info()
        logger.info(f"System Info: {info}")
        time.sleep(1)
