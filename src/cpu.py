from cpuinfo import get_cpu_info

# get cpu information
cpu = get_cpu_info()


def get_name():
    return cpu['brand_raw']


def get_core_count():
    return cpu['count']


def get_arch():
    return cpu['arch']


def get_flags():
    return cpu['flags']


def get_caches():
    cache_idx = {
        0: "l1_data_cache_size",
        1: "l1_instruction_cache_size",
        2: "l2_cache_size",
        3: "l3_cache_size"
    }

    caches = []
    for idx in range(len(cache_idx)):
        try:
            caches.append(cpu[cache_idx[idx]])
        except KeyError:
            caches.append("Unknown value")

    return caches
