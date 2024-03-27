import subprocess
import os
import time
from pathlib import Path

from collect_and_download import *
from utils import *

base_path = Path(__file__).resolve().parent

def load_trace(p):
    return list(map(int, Path(p).read_text().splitlines()))

def dump_trace(trace, p):
    Path(p).write_text('\n'.join(map(str, trace)) + '\n')

def deploy():
    pass

def with_locust(output_folder, locustfile, url, workers):
    print('Starting Workers')
    args = [
        'locust',
        '--worker',
        '-f', locustfile,
    ]
    worker_ps = []
    for i in range(workers):
        worker_ps.append(subprocess.Popen(args, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL))

    print('Starting Master')
    args = [
        'locust',
        '--master',
        '--expect-workers', f'{workers}',
        '--headless',
        '-f', locustfile,
        '-H', url,
        '--csv', output_folder/'locust',
        '--csv-full-history',
        # '--stop-timeout', '30s',
    ]
    master_p = subprocess.Popen(args, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

    time.sleep(1)
    return master_p, worker_ps

def generate_rps(output_folder, rps=-1):
    request_log_file = open(output_folder/'request.log', 'w')
    print('Generating RPS trace')
    warmup_seconds = 10
    trace = load_trace(base_path / 'traces/diurnal-2.txt') if rps == -1 else [rps] * 60
    warmup = []
    for i in range(warmup_seconds):
        rps = round(trace[0] * 1.1 ** ((i - warmup_seconds) / 5))  # x1.1 every 5 seconds, see section A.7 in the paper
        if rps < 1:
            rps = 1
        warmup.append(rps)
    trace = warmup + trace
    # trace = [x // 10 for x in trace]
    dump_trace(trace[:60], base_path / 'rps.txt')

def run_locust(locustfile, url, output_folder, rps=-1):
    generate_rps(output_folder, rps)

    print('Running Locust')

    p, worker_ps = with_locust(output_folder, locustfile, url, workers=8)
    print('Locust started')
    p.wait()
    for wp in worker_ps:
        wp.wait()
    print('Locust finished')
    
def get_data(path, filename='data.zip'):
    start_collect()
    wait_for_completion()
    download_data(path, filename)

def run(algo='round-robin', rps=-1, times=0):
    if os.path.exists('output'):
        os.system('rm -rf output')
    for t in range(times):
        start_time = get_time()
        path = base_path / Path(f'output/{algo}/RPS_{rps}/{start_time}/')
        path.mkdir(parents=True, exist_ok=True)
        # deploy(algo)
        # os.system(f"(cd ../social-network/ && python3 scripts/init_social_graph.py)")
        
        run_locust(base_path / 'locustfile.py', 'http://node0:30001', path, rps=rps)
        end_time = get_time()
        get_data(path, f'{algo}-RPS_{rps}-{get_time()}.zip')
        os.system(f"mv {base_path}/output/{algo}/RPS_{rps}/{start_time} {base_path}/output/{algo}/RPS_{rps}/{start_time}_{end_time}")
        time.sleep(10)

if __name__ == '__main__':
    run(times=3, rps=10)