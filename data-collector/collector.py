from flask import Flask, send_file, jsonify
import threading
import os

from utils import *

app = Flask(__name__)

# 文件和目录设置
data_dir = 'collected_data'
if not os.path.exists(data_dir):
    os.makedirs(data_dir)
zip_filename = 'collected_data.zip'



# 定义一个路由来触发数据收集
@app.route('/collect', methods=['GET'])
def trigger_data_collection():
    thread = threading.Thread(target=collect_and_compress_data)
    thread.start()
    return jsonify({'message': 'Data collection initiated'}), 202

# 定义一个路由来提供数据下载
@app.route('/download', methods=['GET'])
def download_data():
    if not os.path.exists(zip_filename):
        return jsonify({'error': 'Data not available. Please initiate collection first.'}), 404
    return send_file(zip_filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
