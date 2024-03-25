from utils import *
from update_status import update_status
from log_sys_info import log_sys_info
from flask_app import app


if __name__ == "__main__":
    # Starting UDP server in a separate thread
    import threading
    update_status_thread = threading.Thread(target=update_status, daemon=True)
    log_thread = threading.Thread(target=log_sys_info, daemon=True)

    update_status_thread.start()
    log_thread.start()
    
    # Waiting for the server thread to finish
    app.run(host='0.0.0.0', port=SERVICE_PORT)
