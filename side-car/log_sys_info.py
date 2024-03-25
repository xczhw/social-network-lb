import json
import time

from utils import *

# # 创建一个logger
# def get_logger(path, filename):
#     create_if_not_exists(path)
#     filepath = f"{path}/{filename}"
#     logger = logging.getLogger(filepath)
#     logger.setLevel(logging.INFO)
#     handler = logging.FileHandler(filepath)
#     formatter = logging.Formatter('%(asctime)s - %(message)s')
#     handler.setFormatter(formatter)
#     logger.addHandler(handler)
#     return logger

# 写入系统信息
def log_sys_info():
    create_if_not_exists(LOGPATH)
    with open(f'{LOGPATH}/sys_info.jsonl', 'w') as f:
        pass
    while True:
        info = get_sys_info()
        with open(f'{LOGPATH}/sys_info.jsonl', 'a') as f:
            f.write(json.dumps(info) + '\n')
        time.sleep(1)
