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

    ips = []
    for svc in SVC_NAMES:
        ips.extend(get_pod_ips(svc))
    # 创建UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2)  # 设置超时时间

    for ip, port, svc_name in ips:
        try:
            sock.sendto(b'collect', (ip, port))
            data = recv_until_eof(sock)
            # Directly save the received data (now without the EOF marker) as a zip file.
            # if DATA_DIR/svc_name folder does not exist, create it
            path = os.path.join(DATA_DIR, svc_name)
            create_if_not_exists(path)
            with open(os.path.join(path, f'{ip}.zip'), 'wb') as file:
                file.write(data)
        except socket.timeout:
            print(f'No response from {svc_name}')
        except Exception as e:
            print(f'Error with {svc_name}: {e}')

    sock.close()
    
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
    else:
        requested_filename = request.args.get('filename', 'collection_data.zip')
        create_zip_file(DATA_DIR, zip_filename=requested_filename)
        return send_file(requested_filename, as_attachment=True) 
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
