from kubernetes import client, config
import time
import requests

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
    return split_and_strip(safe_read(file_path))

# 初始化k8s客户端
config.load_incluster_config()
v1 = client.CoreV1Api()
# 获取服务中的所有pod的ip
def get_pod_ips(service_name, namespace='social-network'):
    pods = v1.list_namespaced_pod(namespace)
    while not pods.items:
        print(f"No pod found for service {service_name}, retrying in 5 seconds")
        time.sleep(5)
        pods = v1.list_namespaced_pod(namespace)
    # 获取svc中所有的pod
    svc_pods = list(filter(lambda pod: pod.metadata.labels.get('name') == service_name, pods.items))
    # 获取pod的ip
    pod_ips = [pod.status.pod_ip for pod in svc_pods]
    # 过滤掉None
    pod_ips = list(filter(lambda ip: ip is not None, pod_ips))
    create_if_not_exists(f"{DATAPATH}/{service_name}")
    safe_write("\n".join(pod_ips), f"{DATAPATH}/{service_name}/pod_ips.txt")
    return pod_ips

# 向指定ip发送请求
def send_and_recv(route, ip, timeout=2):
    res = requests.get(f"http://{ip}:{SERVICE_PORT}/{route}", timeout=timeout)
    return res.json()

# 向服务中的所有pod发送请求
def send_request_to_all_pod_in_svc(svc, message):
    pod_ips = get_pod_ips(svc)
    response = {}
    for ip in pod_ips:
        res = send_and_recv(message, ip)
        response[ip] = res
    return response

# 保存请求的响应到文件
def save_response_to_file(response, svc, filename, keyword=None):
    create_if_not_exists(f"{DATAPATH}/{svc}")
    if keyword:
        data = "\n".join([f"{ip} {response[ip][keyword]}" for ip in response])
    else:
        data = "\n".join([f"{ip} {response[ip]}" for ip in response])
    safe_write(data, f"{DATAPATH}/{svc}/{filename}")

# 定时更新服务状态
def update_status():
    service_names = get_svc_list()
    while True:
        for svc in service_names:
            # 获取所有下游服务的cpu使用率
            res = send_request_to_all_pod_in_svc(svc, "info")
            save_response_to_file(res, svc, "cpu_usage.txt", "cpu_usage")
            time.sleep(10)
