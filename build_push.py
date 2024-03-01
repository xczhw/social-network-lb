# docker build 

import os
import json
import subprocess

HOST = "node0:5000"

def find_sha256(image_name):
    result = subprocess.run(
        ["docker", "images", '--digests'],
        stdout=subprocess.PIPE,  # 捕获标准输出
        text=True  # 返回的输出作为字符串处理
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

if __name__ == '__main__':
    args = os.sys.argv
    print(args)
    if len(args) > 1 and args[1] == '--rm':
        os.system(f"(cd deploy && bash rm.sh)")
        exit(0)

    sidecar_sha256 = build_side_car()
    deathstarbench_sha256 = build_deathstarbench()
    with open('deploy/image.json', 'w') as f:
        json.dump({
            "sidecar": f'{HOST}/sidecar:latest@sha256:{sidecar_sha256}',
            "deathstarbench": f'{HOST}/deathstarbench:latest@sha256:{deathstarbench_sha256}'
        }, f)
    os.system("(cd deploy && bash deploy.sh)")