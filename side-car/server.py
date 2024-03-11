import socket
from utils import *

# UDP服务端, 接收请求并返回相应的数据
def udp_server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind(('0.0.0.0', SERVICE_PORT))
        while True:
            data, addr = s.recvfrom(1024)
            if data:
                message = data.decode()
                if message.lower() == 'cpu_usage':
                    cpu_usage = get_sys_info()["cpu_usage"]
                    s.sendto(str(cpu_usage).encode(), addr)
                    print('send:' + str(cpu_usage))
                elif message == 'get_log':
                    data = safe_read(f'{LOGPATH}/log.txt', 'rb')
                    while data:
                        s.sendto(data[:1024], addr)
                        data = data[1024:]
                s.sendto('<EOF>'.encode(), (addr))