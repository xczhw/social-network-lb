import requests
import time
import zipfile
import io

if __name__ == '__main__':
    # Flask应用的外部访问地址和端口
    base_url = 'http://node0:30002'

    # 向Flask应用发送请求以开始数据收集
    collect_response = requests.get(f'{base_url}/collect')
    if collect_response.status_code == 202:
        print('Data collection initiated...')
    else:
        print('Failed to initiate data collection:', collect_response.text)
        exit()

    # 轮询以检查数据收集状态
    while True:
        status_response = requests.get(f'{base_url}/status')
        if status_response.status_code == 200:
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
    download_response = requests.get(f'{base_url}/download')
    if download_response.status_code == 200:
        # 解压缩从服务端接收的ZIP数据
        zip_file = zipfile.ZipFile(io.BytesIO(download_response.content))
        zip_file.extractall('downloaded_data')  # 解压数据到 'downloaded_data' 目录
        print('Data downloaded and extracted successfully.')
    else:
        print('Failed to download data:', download_response.text)
