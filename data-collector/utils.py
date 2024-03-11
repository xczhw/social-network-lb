import socket
import zipfile
import time
import os

data_dir = 'collected_data'
if not os.path.exists(data_dir):
    os.makedirs(data_dir)
zip_filename = 'collected_data.zip'

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



def get_svc():
    # TODO: 从k8s API获取服务列表
    services = [
        ('192.168.1.1', 12345, 'svc_name1'),
        ('192.168.1.2', 12345, 'svc_name2'),
        # 在此处添加更多服务
    ]
    return services
