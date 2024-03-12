import os
import fcntl
import psutil
import zipfile

ROOTPATH = '/share'
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

def split_and_strip(data):
    return [x.strip() for x in data.strip().split('\n')]

def safe_read(path, mode='r'):
    with open(path, mode) as f:
        fcntl.flock(f, fcntl.LOCK_SH)
        data = f.read()
        fcntl.flock(f, fcntl.LOCK_UN)
    return data

def safe_write(data, path, mode='w'):
    with open(path, mode) as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.write(data)
        f.flush()
        fcntl.flock(f, fcntl.LOCK_UN)

def create_zip_file(directory, zip_filename):
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(directory):
            for file in files:
                # Full path to the file
                file_path = os.path.join(root, file)
                # Relative path for the file within the zip
                relative_path = os.path.relpath(file_path, directory)
                zipf.write(file_path, relative_path)