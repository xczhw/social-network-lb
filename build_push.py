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

def build_deathstarbench():
    os.system(f"(docker build -t {HOST}/deathstarbench:latest .)")
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

    deathstarbench_sha256 = build_deathstarbench()
    with open('deploy/image.json', 'w') as f:
        json.dump({
            "deathstarbench": f'{HOST}/deathstarbench:latest@sha256:{deathstarbench_sha256}'
        }, f)
    os.system("(cd deploy && bash deploy.sh)")
