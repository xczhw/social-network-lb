import json
import os
from pathlib import Path
from matplotlib import pyplot as plt

from utils import *

current_dir = Path(__file__).resolve().parent

def get_data():
    base_path = current_dir / 'output'
    data = RunData()
    for algo in ['round-robin', 'random', 'weighted']:
        for rps in [-1]:
            rps_path = base_path / algo / f'RPS_{rps}'
            if not rps_path.exists():
                continue
            for run_time_path in rps_path.iterdir():
                file = run_time_path / 'request.log'
                with open(file, 'r') as f:
                    lines = f.readlines()
                for line in lines:
                    d = json.loads(line)
                    data.add_entry(algo, rps, run_time_path.name, (int(d['time']), float(d['latency'])))
    return data

def clean_data(input_data: RunData):
    cleaned_data = RunData()
    for algo, rps_data in input_data.data.items():
        for rps, run_time_data in rps_data.items():
            for run_time, data in run_time_data.items():
                for d in data:
                    if not time_in_range(d[0], run_time):
                        continue
                    cleaned_data.add_entry(algo, rps, run_time, d)
    return cleaned_data

def draw(input_data: RunData):
    for algo, rps_data in input_data.data.items():
        for rps, run_time_data in rps_data.items():
            for run_time, data in run_time_data.items():
                plt.figure()
                x = []
                y = []
                data.sort(key=lambda x: x[0])
                for d in data:
                    x.append(d[0])
                    y.append(d[1])
                plt.plot(x, y, label='run_time')
                plt.legend()
                plt.savefig(current_dir/'output'/algo/f'RPS_{rps}'/run_time/'latency.png')
                print(f'Saved {algo}/RPS_{rps}/{run_time}/latency.png')

def draw_latency():
    data = get_data()
    data = clean_data(data)
    draw(data)

if __name__ == '__main__':
    draw_latency()