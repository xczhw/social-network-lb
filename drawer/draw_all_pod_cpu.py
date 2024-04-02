import json
import os
from pathlib import Path
from matplotlib import pyplot as plt

from utils import *

current_dir = Path(__file__).resolve().parent

def get_data():
    base_path = current_dir / 'output'
    data = PodData()
    for algo in ['round-robin', 'random', 'weighted']:
        for rps in [-1, 10]:
            rps_path = base_path / algo / f'RPS_{rps}'
            if not rps_path.exists():
                continue
            for run_time_path in rps_path.iterdir():
                file = run_time_path / 'pod_logs.jsonl'
                with open(file, 'r') as f:
                    lines = f.readlines()
                for line in lines:
                    d = json.loads(line)
                    for svc_name, pod_data_list in d['pods'].items():
                        for pod_data in pod_data_list:
                            data.add_entry(algo, rps, run_time_path.name, svc_name, pod_data['ip'], (int(d['time']), float(pod_data['cpu'])))
    return data

def clean_data(input_data: PodData):
    cleaned_data = PodData()
    for algo, rps_data in input_data.data.items():
        for rps, run_time_data in rps_data.items():
            for run_time, pod_name_data in run_time_data.items():
                for svc_name, pod_ip_data in pod_name_data.items():
                    for pod_ip, data in pod_ip_data.items():
                        for d in data:
                            if not time_in_range(d[0], run_time):
                                continue
                            cleaned_data.add_entry(algo, rps, run_time, svc_name, pod_ip, d)
    return cleaned_data

def draw(input_data: PodData):
    for algo, rps_data in input_data.data.items():
        for rps, run_time_data in rps_data.items():
            for run_time, pod_name_data in run_time_data.items():
                plt.figure()
                save_path = current_dir / 'output' / algo / f'RPS_{rps}' / run_time
                for svc_name, pod_ip_data in pod_name_data.items():
                    if not save_path.exists():
                        continue
                    for pod_ip, data in pod_ip_data.items():
                        x = []
                        y = []
                        tot = 0 
                        for d in data:
                            tot += 1
                            x.append(tot)
                            y.append(d[1])
                        plt.plot(x, y, label=svc_name + pod_ip)
                # 把legend放在框外面
                plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
                plt.savefig(save_path/'all_pod_cpu_usage.png')
                plt.close()
                print(f'Saved {save_path/"all_pod_cpu_usage.png"}')

def draw_all_pod_cpu():
    data = get_data()
    data = clean_data(data)
    draw(data)

if __name__ == '__main__':
    draw_all_pod_cpu()