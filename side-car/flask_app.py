from flask import Flask, send_file, jsonify
import os

from utils import *

app = Flask(__name__)

@app.route('/download', methods=['GET'])
def download_data():
    create_zip_file(ROOTPATH, 'data.zip')
    return send_file('data.zip', as_attachment=True)

@app.route('/info', methods=['GET'])
def check_info():
    return jsonify(get_sys_info())

# @app.route('/log', methods=['GET'])
# def get_log():
#     return send_file(f'{LOGPATH}/log.txt', as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)  # Ensure the port matches your Kubernetes service configuration
