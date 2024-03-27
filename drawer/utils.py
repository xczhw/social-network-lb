import zipfile
from collections import defaultdict

def unzip(path, filename):
    try:
        with zipfile.ZipFile(path / filename, 'r') as zip_ref:
            zip_ref.extractall(path / filename.strip('.zip'))
    except Exception as e:
        print(e)
        print('Error unzipping', path, filename)
        pass

def get_subdir(path):
    return [item for item in path.iterdir() if item.is_dir()]

def time_in_range(timestamp, time_range):
    t = time_range.split('_')
    if timestamp < int(t[0]):
        return False
    if len(t) > 1 and timestamp > int(t[1]):
        return False
    return True

def nested_defaultdict(levels, final_type=list):
    if levels == 1:
        return defaultdict(final_type)
    else:
        return defaultdict(lambda: nested_defaultdict(levels - 1, final_type))

class RunData:
    def __init__(self):
        self.data = nested_defaultdict(3, final_type=list)

    def add_entry(self, algo, rps, run_time, data):
        self.data[algo][rps][run_time].append(data)

class PodData:   
    def __init__(self):
        # 使用defaultdict避免深层嵌套和多级字典检查
        self.data = nested_defaultdict(5, final_type=list)

    def add_entry(self, algo, rps, run_time, service_path, pod_name, data):
        # 直接添加日志条目到对应的分类中
        self.data[algo][rps][run_time][service_path][pod_name].append(data)

class PodTransData:
    def __init__(self):
        self.data = nested_defaultdict(6, final_type=list)

    def add_entry(self, algo, rps, run_time, service_path, pod_name, aim_pod, data):
        self.data[algo][rps][run_time][service_path][pod_name][aim_pod].append(data)
