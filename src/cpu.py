from cpuinfo import get_cpu_info

# get cpu information
cpu = get_cpu_info()

class CPU:
    def get_name():
        return cpu['brand_raw']
    def get_core_count():
        return cpu['count']
    def get_arch():
        return cpu['arch']
    def get_flags():
        return cpu['flags']
    def get_caches():
        """
        Index:

        "l1_data_cache_size",
        "l1_instruction_cache_size",
        "l2_cache_size",
        "l2_cache_line_size",
        "l2_cache_associativity",
        "l3_cache_size"
        """
        caches = [''] * 6

        try:
            caches[0] = cpu["l1_data_cache_size"]
        except KeyError:
            caches[0] = "Unknown value"

        try:
            caches[1] = cpu["l1_instruction_cache_size"]
        except KeyError:
            caches[1] = "Unknown value"

        try:
            caches[2] = cpu["l2_cache_size"]
        except KeyError: 
            caches[2] = "Unknown value"

        try:
            caches[3] = cpu["l2_cache_line_size"]
        except KeyError:
            caches[3] = "Unknown value"

        try:
            caches[4] = cpu["l2_cache_associativity"]
        except KeyError: 
            caches[4] = "Uknown value"

        try:
            caches[5] = cpu["l3_cache_size"]
        except:
            caches[5] = "Unknown value"

        return caches