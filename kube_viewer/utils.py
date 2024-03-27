import subprocess
import time

CUSTOM_EPOCH=1514764800000
def get_time():
    return int((time.time() * 1000) - CUSTOM_EPOCH)

# 运行命令，获取命令行输出
def get_cmd_output(command):
    try:
        output = subprocess.check_output(command, shell=True, text=True)
        return output
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")
        return None

# 单位换算
def convert_resources(cpu, memory):
    # Convert CPU from millicores to cores
    cpu_cores = float(cpu.replace('m', '')) / 1000

    # Convert Memory from Mi/Gi to Bytes
    if 'Mi' in memory:
        memory_bytes = float(memory.replace('Mi', '')) * 1024**2
    elif 'Gi' in memory:
        memory_bytes = float(memory.replace('Gi', '')) * 1024**3
    else:
        memory_bytes = float(memory)  # Assumes bytes if no unit

    return cpu_cores, memory_bytes

def get_pod_ips():
    command = "kubectl get pod -o wide"
    output = get_cmd_output(command)
    lines = output.strip().split('\n')
    
    if len(lines) < 2:
        return {}
    
    headers = lines[0].split()
    try:
        name_index = headers.index('NAME')
        ip_index = headers.index('IP')
    except ValueError:
        print("IP column not found in output")
        return {}
    
    pod_ips = {}
    for line in lines[1:]:
        parts = line.split()
        if len(parts) > ip_index:
            pod_name = parts[name_index]
            pod_ip = parts[ip_index]
            pod_ips[pod_name] = pod_ip
    
    return pod_ips

# 获取pod信息
def get_pod_info():
    command = "kubectl top pod"
    output = get_cmd_output(command)
    while output is None:
        output = get_cmd_output(command)
        time.sleep(1)

    timestamp = get_time()
    pod_ips = get_pod_ips()

    lines = output.strip().split('\n')[1:]
    result = {}
    for line in lines:
        parts = line.split()
        pod_type = '-'.join(parts[0].split('-')[:-2])
        if pod_type not in result:
            result[pod_type] = []
        cpu, memory = parts[1], parts[2]
        cpu_cores, memory_bytes = convert_resources(cpu, memory)
        pod_info = {'name': parts[0], 'cpu': cpu_cores, 'memory': memory_bytes}
        if pod_ips:
            pod_info['ip'] = pod_ips.get(parts[0], 'Unknown')
        result[pod_type].append(pod_info)
    return {'time': timestamp, 'pods': result}

# 获取节点信息
def get_node_info():
    command = "kubectl top node"
    output = get_cmd_output(command)
    while output is None:
        output = get_cmd_output(command)
        time.sleep(1)
    timestamp = get_time()

    lines = output.strip().split('\n')[1:]
    result = []
    for line in lines:
        parts = line.split()
        cpu, memory = parts[1], parts[3]
        cpu_cores, memory_bytes = convert_resources(cpu, memory)
        cpu_usage = float(parts[2].replace('%', ''))
        memory_usage = float(parts[4].replace('%', ''))
        node_info = {'name': parts[0], 'cpu': cpu_cores, 'memory': memory_bytes, 'cpu_usage': cpu_usage, 'memory_usage': memory_usage}
        result.append(node_info)
    return {'time': timestamp, 'nodes': result}

