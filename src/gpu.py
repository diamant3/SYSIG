import GPUtil
import pyadl


def get_name():
    gpu_list = []

    # amd
    amd = pyadl.ADLManager.getInstance().getDevices()
    for gpu in amd:
        gpu_list.append(gpu.adapterName)
    # nvidia
    nvidia = GPUtil.getGPUs()
    for gpu in nvidia:
        gpu_list.append(gpu.name)

    return gpu_list
