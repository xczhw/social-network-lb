import socket
import json
import time
from kubernetes import client, config
import psutil
import logging
import os

DATAPATH = '/share/data'
LOGPATH = '/share/logs'
SERVICE_PORT = int(os.environ.get('SERVICE_PORT'))

def create_if_not_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)

def get_logger(path, filename):
    create_if_not_exists(path)
    filepath = path + filename
    logger = logging.getLogger(filepath)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(filepath)
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

logger = get_logger(LOGPATH, 'log.txt')

def get_pod_ips(service_name, namespace='default'):
    pod_ips = []
    pods = v1.list_namespaced_pod(namespace)
    for pod in pods.items:
        if pod.metadata.labels.get('name') == service_name:
            pod_ips.append(pod.status.pod_ip)
    create_if_not_exists(f"{DATAPATH}/{service_name}")
    with open(f"{DATAPATH}/{service_name}/pod_ips.txt", 'w') as f:
        f.write("\n".join(pod_ips))
    return pod_ips

# Function to get system information (like CPU usage)
def get_system_info():
    return {
        "cpu_usage": psutil.cpu_percent(interval=1)
    }

# UDP Server to handle incoming requests
def udp_server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind(('0.0.0.0', SERVICE_PORT))
        while True:
            data, addr = s.recvfrom(1024)
            if data:
                message = data.decode()
                if message.lower() == 'cpu_usage':
                    cpu_usage = get_system_info()["cpu_usage"]
                    s.sendto(str(cpu_usage).encode(), addr)
                    print('send:' + cpu_usage)
                elif message == 'get_log':
                    with open(f'{LOGPATH}/log.txt', 'rb') as f:
                        s.sendto(f.read(), addr)
                s.sendto('<EOF>', (addr))

# Function to send request to other pods
def send_request_to_all_pod_in_svc(svc, message):
    pod_ips = get_pod_ips(svc)
    response = {}
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        for ip in pod_ips:
            s.sendto(message.encode(), (ip, SERVICE_PORT))
            data, _ = s.recvfrom(1024)
            # print(f"Response from {ip}: {data.decode()}")
            response[ip] = data.decode()
    return response

# waiting until file exists
def wait_for_file(file_path, timeout=60):
    start_time = time.time()
    while not os.path.exists(file_path):
        if time.time() - start_time >= timeout:
            raise TimeoutError(f"File {file_path} not found after {timeout} seconds")
        time.sleep(5)

def get_svc_list():
    file_path = f'{DATAPATH}/svc_list.txt'
    wait_for_file(file_path)
    with open(file_path, 'r') as f:
        return [svc.strip() for svc in f.readlines()]

def save_response_to_file(response, svc, filename):
    create_if_not_exists(f"{DATAPATH}/{svc}")
    with open(f"{DATAPATH}/{svc}/{filename}", 'w') as f:
        json.dump(response, f)

# Main function
def update_status():
    service_names = get_svc_list()
    while True:
        for svc in service_names:
            res = send_request_to_all_pod_in_svc(svc, "cpu_usage")
            save_response_to_file(res, svc, "cpu_usage.txt")
            time.sleep(10)

def log_system_info():
    while True:
        info = get_system_info()
        logger.info(f"System Info: {info}")
        time.sleep(1)

if __name__ == "__main__":
    # Kubernetes client initialization
    config.load_incluster_config()
    v1 = client.CoreV1Api()

    # Starting UDP server in a separate thread
    import threading
    server_thread = threading.Thread(target=udp_server, daemon=True)
    update_status_thread = threading.Thread(target=update_status, daemon=True)
    log_thread = threading.Thread(target=log_system_info, daemon=True)

    server_thread.start()
    update_status_thread.start()
    log_thread.start()
