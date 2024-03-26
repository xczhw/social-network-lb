from utils import *
from pathlib import Path
import os

def unzip_output():
    # 使用__file__确定当前文件的绝对路径，然后找到它的父目录
    base_path = Path(__file__).parent.resolve() / 'output'
    for algo in ['round-robin', 'random', 'weighted']:
        for rps in [-1]:
            rps_path = base_path / algo / f'RPS_{rps}'
            if not rps_path.exists():
                continue
            for run_time in rps_path.iterdir():
                for service_path in run_time.iterdir():
                    if not service_path.is_dir():
                        continue
                    for file in service_path.glob('*.zip'):  # 直接寻找zip文件
                        unzip(service_path, file.name)

def move_output():
    # 同样使用__file__避免路径错误
    current_dir = Path(__file__).parent.resolve()
    locust_output_path = current_dir.parent / 'locust' / 'output'
    output_path = current_dir / 'output'

    if not locust_output_path.exists():
        print('Locust output folder not found.')
        return
    
    if not output_path.exists():
        os.system(f'mv "{locust_output_path}" "{output_path}"')
    else:
        print('Output folder already exists. Do you want to overwrite it [Y/n] ?')
        choice = input()
        if choice.lower() == 'y' or choice == '':
            os.system(f'rm -rf "{output_path}"')
            os.system(f'mv "{locust_output_path}" "{output_path}"')
        else:
            print('Aborted.')
            exit(0)

if __name__ == '__main__':
    move_output()
    unzip_output()
    