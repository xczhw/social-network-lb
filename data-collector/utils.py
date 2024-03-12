from kubernetes import client, config
import socket
import zipfile
import time
import os

DATA_DIR = 'collected_data'
SVC_NAMES = ['unique-id-service', 'compose-post-service']

def create_if_not_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)

create_if_not_exists(DATA_DIR)

def recv_until_eof(sock):
    full_data = bytearray()
    while True:
        data, server = sock.recvfrom(4096)  # Adjust based on your network environment
        if data.endswith(b'<EOF>'):  # Check if the end of the file marker is present
            if len(data) > 5:
                full_data.extend(data[:-5])
            break
        full_data.extend(data)
    return full_data

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
    pod_ips = [(pod.status.pod_ip, 5050, service_name) for pod in svc_pods] #TODO: 可能会换端口
    # 过滤掉None
    pod_ips = list(filter(lambda ip: ip[0] is not None, pod_ips))
    return pod_ips

def create_zip_file(directory, zip_filename):
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(directory):
            for file in files:
                # Full path to the file
                file_path = os.path.join(root, file)
                # Relative path for the file within the zip
                relative_path = os.path.relpath(file_path, directory)
                zipf.write(file_path, relative_path)
