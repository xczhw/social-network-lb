
import json
import os
import time

from utils import *
from pathlib import Path

def main():
    base_path = Path(__file__).resolve().parent / 'output'
    if base_path.exists():
        os.system(f'rm -rf {base_path}')
    base_path.mkdir(parents=True, exist_ok=True)

    pod_log_path = base_path / 'pod_logs.jsonl'
    node_log_path = base_path / 'node_logs.jsonl'
    while True:
        pod_info = get_pod_info()
        node_info = get_node_info()

        with open(pod_log_path, 'a') as f:
            f.write(json.dumps(pod_info) + '\n')
        with open(node_log_path, 'a') as f:
            f.write(json.dumps(node_info) + '\n')
    
        time.sleep(1)

if __name__ == "__main__":
    main()
