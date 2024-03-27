from utils import *
from pathlib import Path
import os
from draw_cpu import draw_cpu
from draw_latency import draw_latency
from draw_send_to import draw_send_to

def unzip_output():
    base_path = Path(__file__).parent.resolve() / 'output'
    for algo in ['round-robin', 'random', 'weighted']:
        for rps in [-1, 10]:
            rps_path = base_path / algo / f'RPS_{rps}'
            if not rps_path.exists():
                continue
            for run_time in rps_path.iterdir():
                for service_path in run_time.iterdir():
                    if not service_path.is_dir():
                        continue
                    for file in service_path.glob('*.zip'):  # 直接寻找zip文件
                        print(f'Unzipping {file}')
                        unzip(service_path, file.name)

def move_output():
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

if __name__ == '__main__':
    move_output()
    unzip_output()
    draw_cpu()
    draw_latency()
    draw_send_to()
    