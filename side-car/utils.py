import os
import psutil

DATAPATH = '/share/data'
LOGPATH = '/share/logs'
SERVICE_PORT = int(os.environ.get('SERVICE_PORT'))

def create_if_not_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)

def get_sys_info():
    return {
        "cpu_usage": psutil.cpu_percent(interval=1)
    }