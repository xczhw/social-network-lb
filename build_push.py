# docker build 

import os
import json
import subprocess

from pathlib import Path

HOST = "node0:5000"

base_path = Path(__file__).resolve().parent

def find_sha256(image_name):
    result = subprocess.run(
        ["docker", "images", '--digests'],
        stdout=subprocess.PIPE,  # cache stdio
        text=True  # the returned output save as string.
    )
    for line in result.stdout.split('\n'):
        if image_name in line and 'latest' in line:
            sha256 = line.split()[2][len('sha256:'):]
            return sha256
    return None

def build_side_car():
    os.system(f"(cd side-car && docker build -t {HOST}/sidecar:latest .)")
    # push and get sha256
    os.system(f"docker push {HOST}/sidecar:latest")
    sha256 = find_sha256(f"{HOST}/sidecar")
    if sha256 is None:
        raise Exception("sidecar sha256 not found")
    return sha256

def build_deathstarbench():
    os.system(f"(cd social-network && docker build -t {HOST}/deathstarbench:latest .)")
    # push and get sha256
    os.system(f"docker push {HOST}/deathstarbench:latest")
    sha256 = find_sha256(f"{HOST}/deathstarbench")
    if sha256 is None:
        raise Exception("deathstarbench sha256 not found")
    return sha256

def build_data_collector():
    os.system(f"(cd data-collector && docker build -t {HOST}/datacollector:latest .)")
    # push and get sha256
    os.system(f"docker push {HOST}/datacollector:latest")
    sha256 = find_sha256(f"{HOST}/datacollector")
    if sha256 is None:
        raise Exception("datacollector sha256 not found")
    return sha256
    
def del_viewer(session_name="kube_top_log"):
    # 检查是否存在指定名称的 screen 会话
    check_command = f"screen -ls | grep {session_name}"
    try:
        # 如果下面的命令成功，说明会话存在
        subprocess.check_output(check_command, shell=True, text=True)
        # 删除现有的 screen 会话
        kill_command = f"screen -S {session_name} -X quit"
        subprocess.check_call(kill_command, shell=True)
        print(f"Existing screen session '{session_name}' has been terminated.")
        if (base_path / 'kube_viewer' / 'output').exists:
            os.system(f"rm -rf {base_path / 'kube_viewer' / 'output'}")
    except subprocess.CalledProcessError:
        # 如果会话不存在，就会抛出异常，这里不做任何操作
        print(f"No existing screen session named '{session_name}'.")

def run_viewer(session_name="kube_top_log"):
    script_path = "kube_viewer/viewer.py"
    
    del_viewer(session_name)
    # create a new screen and run script here
    create_command = f"screen -S {session_name} -d -m bash -c 'python3 {script_path}; exec bash'"
    try:
        subprocess.check_call(create_command, shell=True)
        print(f"Script {script_path} is now running in a new screen session called '{session_name}'")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while starting the script in a new screen session: {e}")


if __name__ == '__main__':
    args = os.sys.argv
    print(args)
    if len(args) > 1 and args[1] == '--rm':
        os.system(f"(cd deploy && bash rm.sh)")
        del_viewer()
        exit(0)

    sidecar_sha256 = build_side_car()
    deathstarbench_sha256 = build_deathstarbench()
    datacollector_sha256 = build_data_collector()
    with open('deploy/image.json', 'w') as f:
        json.dump({
            "sidecar": f'{HOST}/sidecar:latest@sha256:{sidecar_sha256}',
            "deathstarbench": f'{HOST}/deathstarbench:latest@sha256:{deathstarbench_sha256}',
            "datacollector": f'{HOST}/datacollector:latest@sha256:{datacollector_sha256}'
        }, f)
    os.system("(cd deploy && bash deploy.sh)")

    run_viewer()
