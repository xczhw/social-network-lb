import json
import os
from pathlib import Path
from matplotlib import pyplot as plt

from utils import *

current_dir = Path(__file__).resolve().parent

def get_data():
    base_path = current_dir / 'output'
    data = PodTransData()
    for algo in ['round-robin', 'random', 'weighted']:
        for rps in [-1, 10]:
            rps_path = base_path / algo / f'RPS_{rps}'
            if not rps_path.exists():
                continue
            for run_time_path in rps_path.iterdir():
                for service_path in get_subdir(run_time_path):
                    for pod_path in get_subdir(service_path):
                        for aim_path in get_subdir(pod_path/'logs'):
                            file = aim_path / 'send_to.txt'
                            if not file.exists():
                                continue
                            with open(file, 'r') as f:
                                lines = f.readlines()
                            for line in lines:
                                d = line.split()
                                data.add_entry(algo, rps, run_time_path.name, service_path.name, pod_path.name, aim_path.name, (int(d[0]), d[1]))
    return data

def clean_data(input_data: PodTransData):
    cleaned_data = PodTransData()
    for algo, rps_data in input_data.data.items():
        for rps, run_time_data in rps_data.items():
            for run_time, service_path_data in run_time_data.items():
                for service_path, pod_name_data in service_path_data.items():
                    for pod_name, aim_pod_data in pod_name_data.items():
                        for aim_pod, data in aim_pod_data.items():
                            for d in data:
                                if not time_in_range(d[0], run_time):
                                    continue
                                cleaned_data.add_entry(algo, rps, run_time, service_path, pod_name, aim_pod, d)
                        
    return cleaned_data

def draw(input_data: PodData):
    for algo, rps_data in input_data.data.items():
        for rps, run_time_data in rps_data.items():
            for run_time, service_path_data in run_time_data.items():
                for service_path, pod_name_data in service_path_data.items():
                    for pod_name, aim_pod_data in pod_name_data.items():
                        plt.figure()
                        for aim_pod, data in aim_pod_data.items():
                            tot = {}
                            for d in data:
                                if d[1] not in tot:
                                    tot[d[1]] = 0
                                tot[d[1]] += 1
                            bars = plt.bar(tot.keys(), tot.values(), label=aim_pod)
                            for bar in bars:
                                height = bar.get_height()
                                plt.text(bar.get_x() + bar.get_width()/2, height, height, ha='center', va='bottom')
                        plt.legend()
                        plt.savefig(current_dir/'output'/algo/f'RPS_{rps}'/run_time/service_path/pod_name/'send_to.png')
                        print(f'Saved {algo}/RPS_{rps}/{run_time}/{service_path}/{pod_name}/send_to.png')

def draw_send_to():
    data = get_data()
    data = clean_data(data)
    draw(data)

if __name__ == '__main__':
    draw_send_to()