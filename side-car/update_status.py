from kubernetes import client, config
import time
import socket

from utils import *

# 等待文件出现
def wait_for_file(file_path, timeout=60):
    start_time = time.time()
    while not os.path.exists(file_path):
        if time.time() - start_time >= timeout:
            raise TimeoutError(f"File {file_path} not found after {timeout} seconds")
        time.sleep(5)

# 获取服务列表
def get_svc_list():
    file_path = f'{DATAPATH}/svc_file.txt'
    wait_for_file(file_path)
    with open(file_path, 'r') as f:
        return [svc.strip() for svc in f.readlines()]

# 初始化k8s客户端
config.load_incluster_config()
v1 = client.CoreV1Api()
# 获取服务中的所有pod的ip
def get_pod_ips(service_name, namespace='social-network'):
    pods = v1.list_namespaced_pod(namespace)
    svc_pods = list(filter(lambda pod: pod.metadata.labels.get('name') == service_name, pods.items))
    pod_ips = [pod.status.pod_ip for pod in svc_pods]
    pod_ips = list(filter(lambda ip: ip is not None, pod_ips))
    create_if_not_exists(f"{DATAPATH}/{service_name}")
    with open(f"{DATAPATH}/{service_name}/pod_ips.txt", 'w') as f:
        f.write("\n".join(pod_ips))
    return pod_ips


def recv_until_eof(s):
    data_parts = []
    while True:
        data, _ = s.recvfrom(1024)
        data_parts.append(data)
        if data.decode().endswith('<EOF>'):
            break
    data = b''.join(data_parts).decode()
    data = data[:-len('<EOF>')]
    return data

def send_to(ip, message, timeout=2):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.settimeout(timeout)
        try:
            s.sendto(message.encode(), (ip, SERVICE_PORT))
            data = recv_until_eof(s)
            print(f"Response from {ip}: {data}")
        except socket.timeout:
            data = "None"
            print(f"Timeout for {ip}")
    return data

# 向服务中的所有pod发送请求
def send_request_to_all_pod_in_svc(svc, message):
    pod_ips = get_pod_ips(svc)
    response = {}
    for ip in pod_ips:
        res = send_to(ip, message)
        response[ip] = res
    return response

# 保存请求的响应到文件
def save_response_to_file(response, svc, filename):
    create_if_not_exists(f"{DATAPATH}/{svc}")
    with open(f"{DATAPATH}/{svc}/{filename}", 'w') as f:
        for ip in response:
            f.write(f"{ip} {response[ip]}\n")

# 定时更新服务状态
def update_status():
    service_names = get_svc_list()
    while True:
        for svc in service_names:
            res = send_request_to_all_pod_in_svc(svc, "cpu_usage")
            save_response_to_file(res, svc, "cpu_usage.txt")
            time.sleep(10)
