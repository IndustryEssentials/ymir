from typing import Dict, Set

from pynvml import nvmlInit, nvmlDeviceGetCount, nvmlDeviceGetHandleByIndex, nvmlDeviceGetMemoryInfo, nvmlShutdown


def get_gpus_info() -> Dict:
    gpu_info = dict()
    nvmlInit()
    for i in range(nvmlDeviceGetCount()):
        handle = nvmlDeviceGetHandleByIndex(i)
        gpu_mem_info = nvmlDeviceGetMemoryInfo(handle)
        free_percent = gpu_mem_info.free / gpu_mem_info.total
        gpu_info[str(i)] = free_percent
    nvmlShutdown()

    return gpu_info


def get_free_gpus() -> Set:
    gpus_info = get_gpus_info()
    runtime_free_gpus = {i for i, free_percent in gpus_info.items() if free_percent > 0.8}

    return runtime_free_gpus
