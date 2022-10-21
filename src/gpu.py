from GPUtil import *
from pyadl import *

class GPU:
    def get_name():
        gpu_list = []

        # amd
        amd = ADLManager.getInstance().getDevices()
        for gpu in amd:
            gpu_list.append(gpu.adapterName)
        
        # nvidia
        nvidia = getGPUs()
        for gpu in nvidia:
            gpu_list.append(gpu.name)

        return gpu_list
