import time
import shutil
import os

CUSTOM_EPOCH=1514764800000
def get_time():
    return int((time.time() * 1000) - CUSTOM_EPOCH)

def force_move(src, dst):
    if os.path.exists(dst):
        if os.path.isdir(dst):
            shutil.rmtree(dst)
        else:
            os.remove(dst)
    shutil.move(src, dst)