import socket
from utils import *

# UDP Server to handle incoming requests
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
                    with open(f'{LOGPATH}/log.txt', 'rb') as f:
                        while True:
                            chunk = f.read(1024)
                            if not chunk:
                                break
                            s.sendto(chunk, addr)
                s.sendto('<EOF>'.encode(), (addr))