from utils import *
from server import udp_server
from update_status import update_status
from log_sys_info import log_sys_info

DATAPATH = '/share/data'

if __name__ == "__main__":
    # Starting UDP server in a separate thread
    import threading
    server_thread = threading.Thread(target=udp_server)
    update_status_thread = threading.Thread(target=update_status, daemon=True)
    log_thread = threading.Thread(target=log_sys_info, daemon=True)

    server_thread.start()
    update_status_thread.start()
    log_thread.start()
    
    # Waiting for the server thread to finish
    server_thread.join()
