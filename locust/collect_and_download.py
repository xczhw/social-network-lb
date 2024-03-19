import requests
import time
import zipfile
import io
import pathlib
import shutil

from utils import *

# Flask应用的外部访问地址和端口
base_url = 'http://node0:30002'

# 向Flask应用发送请求以开始数据收集
def start_collect():
    collect_response = requests.get(f'{base_url}/collect')
    if collect_response.status_code == 202:
        print('Data collection initiated...')
    else:
        print('Failed to initiate data collection:', collect_response.text)
        exit()

# 轮询以检查数据收集状态
def wait_for_completion():
    while True:
        status_response = requests.get(f'{base_url}/status')
        if status_response.status_code < 400:
            status = status_response.json().get('status')
            if status == 'complete':
                print('Data collection completed.')
                break
            else:
                print('Data collection is in progress...')
        else:
            print('Failed to check data collection status:', status_response.text)
            exit()
        time.sleep(5)  # 等待5秒后再次检查状态

# 数据收集完成后，下载数据
def download_data(save_path=pathlib.Path('downloaded_data'), filename='data.zip'):
    download_response = requests.get(f'{base_url}/download', params={'filename': filename})
    if download_response.status_code == 200:
        # 解压缩从服务端接收的ZIP数据
        zip_file = zipfile.ZipFile(io.BytesIO(download_response.content))
        zip_file.extractall(save_path)  # 解压数据到 'downloaded_data' 目录
        force_move('request.log', save_path/'request.log')
        print('Data downloaded and extracted successfully.')
    else:
        print('Failed to download data:', download_response.text)
