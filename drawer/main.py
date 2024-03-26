from utils import *
from pathlib import Path
import os

def unzip_output():
    base_path = Path('./output')
    for algo in ['round-robin', 'random', 'weighted']:
        for rps in [-1]:
            rps_path = base_path / algo / f'RPS_{rps}'
            if not rps_path.exists():
                continue
            for run_time in rps_path.iterdir():
                for service_path in run_time.iterdir():
                    if not service_path.is_dir():
                        continue
                    for file in service_path.glob('*.zip'):  # 直接寻找csv文件
                        unzip(service_path, file.name)

def move_output():
    if not os.path.exists('../locust/output'):
        print('Locust output folder not found.')
        return
    
    if not os.path.exists('./output'):
        os.system('mv ../locust/output .')
    else:
        print('Output folder already exists. Do you want to overwrite it [Y/n] ?')
        choice = input()
        if choice.lower() == 'y' or choice == '':
            os.system('rm -rf output')
            os.system('mv ../locust/output .')
        else:
            print('Aborted.')
            exit(0)

if __name__ == '__main__':
    move_output()
    unzip_output()
    