import subprocess
import time
import pathlib

def load_trace(p):
    return list(map(int, pathlib.Path(p).read_text().splitlines()))

def dump_trace(trace, p):
    pathlib.Path(p).write_text('\n'.join(map(str, trace)) + '\n')

def deploy():
    pass

def with_locust(temp_dir, locustfile, url, workers):
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
        '--csv', temp_dir/'locust',
        '--csv-full-history',
        # '--stop-timeout', '30s',
    ]
    master_p = subprocess.Popen(args, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

    time.sleep(1)
    return master_p, worker_ps

def run_locust(locustfile, url):
    request_log_file = open('request.log', 'w')
    print('Generating RPS trace')
    warmup_seconds = 10
    trace = load_trace('./traces/diurnal-2.txt')
    warmup = []
    for i in range(warmup_seconds):
        rps = round(trace[0] * 1.1 ** ((i - warmup_seconds) / 5))  # x1.1 every 5 seconds, see section A.7 in the paper
        if rps < 1:
            rps = 1
        warmup.append(rps)
    trace = warmup + trace
    trace = list(map(lambda x: x // 10, trace[:40]))
    dump_trace(trace, 'rps.txt')
    
    print('Running Locust')
    temp_dir = pathlib.Path('output/temp')
    temp_dir.mkdir(parents=True, exist_ok=True)

    p, worker_ps = with_locust(temp_dir, locustfile, url, workers=8)
    print('Locust started')
    p.wait()
    print('Locust finished')
    for wp in worker_ps:
        wp.wait()

def get_data():
    pass

# deploy()
run_locust('./locustfile.py', 'http://node0:30001')
# get_data()