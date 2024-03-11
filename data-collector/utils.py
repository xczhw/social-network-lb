
import socket
import zipfile
import time

def get_svc():
    services = [
        ('192.168.1.1', 12345, 'svc_name1'),
        ('192.168.1.2', 12345, 'svc_name2'),
        # 在此处添加更多服务
    ]
    return services

# 用于收集和压缩数据的函数
def collect_and_compress_data():
    collected_data = {}
    # 创建UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2)  # 设置超时时间

    for ip, port, svc_name in services:
        try:
            server_address = (ip, port)
            sock.sendto(b'collect', server_address)
            data, server = sock.recvfrom(4096)
            collected_data[svc_name] = data.decode()
        except socket.timeout:
            collected_data[svc_name] = 'No response'
        except Exception as e:
            collected_data[svc_name] = f'Error: {e}'

    sock.close()

    # 将收集到的数据写入文件，并压缩
    for svc_name, data in collected_data.items():
        with open(os.path.join(data_dir, f'{svc_name}.txt'), 'w') as file:
            file.write(data)

    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for root, dirs, files in os.walk(data_dir):
            for file in files:
                zipf.write(os.path.join(root, file), arcname=file)
