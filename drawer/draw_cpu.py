from utils import *
import pathlib
import os

def draw():
    for algo in ['round-robin', 'random', 'weighted']:
        for rps in [-1]:
            if not os.path.exists(f'./output/{algo}/RPS_{rps}'):
                continue
            for run in os.listdir(f'./output/{algo}/RPS_{rps}'):
                for service in os.listdir(f'./output/{algo}/RPS_{rps}/{run}'):
                    if not os.path.isdir(f'./output/{algo}/RPS_{rps}/{run}/{service}'):
                        continue
                    path = pathlib.Path(f'./output/{algo}/RPS_{rps}/{run}/{service}')
                    for file in os.listdir(path):
                        if file.endswith('.zip'):
                            unzip(path, file)

