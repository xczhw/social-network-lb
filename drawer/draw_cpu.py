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
        for rps in [-1]:
            rps_path = base_path / algo / f'RPS_{rps}'
            if not rps_path.exists():
                continue
            for run_time_path in rps_path.iterdir():
                for service_path in get_subdir(run_time_path):
                    for pod_path in get_subdir(service_path):
                        file = pod_path / 'logs' / 'sys_info.jsonl'
                        with open(file, 'r') as f:
                            lines = f.readlines()
                        for line in lines:
                            d = json.loads(line)
                            data.add_entry(algo, rps, run_time_path.name, service_path.name, pod_path.name, (int(d['time']), float(d['cpu_usage'])))
    return data

def clean_data(input_data: PodData):
    cleaned_data = PodData()
    for algo, rps_data in input_data.data.items():
        for rps, run_time_data in rps_data.items():
            for run_time, service_path_data in run_time_data.items():
                t = run_time.split('_')
                for service_path, pod_name_data in service_path_data.items():
                    for pod_name, data in pod_name_data.items():
                        for d in data:
                            if (d[0] < int(t[0])) or (len(t) > 1 and d[0] > int(t[1])):
                                continue
                            cleaned_data.add_entry(algo, rps, run_time, service_path, pod_name, d)
    return cleaned_data

def draw(input_data: PodData):
    for algo, rps_data in input_data.data.items():
        for rps, run_time_data in rps_data.items():
            for run_time, service_path_data in run_time_data.items():
                for service_path, pod_name_data in service_path_data.items():
                    plt.figure()
                    for pod_name, data in pod_name_data.items():
                        x = []
                        y = []
                        for d in data:
                            x.append(d[0])
                            y.append(d[1])
                        plt.plot(x, y, label=pod_name)
                    plt.legend()
                    plt.savefig(current_dir/'output'/algo/f'RPS_{rps}'/run_time/service_path/'cpu_usage.png')
                    print(f'Saved {algo}/RPS_{rps}/{run_time}/{service_path}/cpu_usage.png')


if __name__ == '__main__':
    data = get_data()
    data = clean_data(data)
    draw(data)