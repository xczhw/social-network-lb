from flask import Flask, send_file, jsonify, request
import socket
import threading
import zipfile
import time

from utils import *

collection_in_progress = False
collection_complete = False

def collect_and_compress_data():
    global collection_in_progress, collection_complete
    collection_in_progress = True
    collection_complete = False

    services = get_svc()
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
    
    collection_in_progress = False
    collection_complete = True

app = Flask(__name__)

@app.route('/collect', methods=['GET'])
def trigger_data_collection():
    global collection_in_progress, collection_complete
    if collection_in_progress:
        return jsonify({'message': 'Data collection is already in progress'}), 409  # 409 Conflict
    else:
        thread = threading.Thread(target=collect_and_compress_data)
        thread.start()
        return jsonify({'message': 'Data collection initiated'}), 202  # Accepted

@app.route('/status', methods=['GET'])
def check_collection_status():
    if collection_complete:
        return jsonify({'status': 'complete'}), 200  # OK
    elif collection_in_progress:
        return jsonify({'status': 'in_progress'}), 202  # Accepted
    else:
        return jsonify({'status': 'not_started'}), 424  # Failed Dependency

@app.route('/download', methods=['GET'])
def download_data():
    if not collection_complete:
        return jsonify({'error': 'Data collection not complete. Please check status.'}), 424  # Failed Dependency
    elif not os.path.exists(zip_filename):
        return jsonify({'error': 'Data file does not exist. Please initiate collection first.'}), 404  # Not Found
    else:
        return send_file(zip_filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
