from flask import Flask, send_file, jsonify, request
import requests
import threading
import zipfile
import pathlib
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

    for ip, port, svc_name in ips:
        response = requests.get(f'http://{ip}:{port}/download')
        path = pathlib.Path(DATA_DIR) / svc_name
        create_if_not_exists(path)
        with open(path / f'{ip}.zip', 'wb') as f:
            f.write(response.content)

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
