from datetime import datetime
import dearpygui.dearpygui as dpg
from cpu import *
from gpu import *
from psutil import *
from platform import uname

cpu = CPU
gpu = GPU

WIN_WIDTH = 1024
WIN_HEIGHT = 640

RED = [255, 0, 0]
BLUE = [0, 0, 255]
GREEN = [0, 255, 0]

def get_size(bytes):
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes <= 1024:
            return f"{bytes:.2f}{unit}B"
        bytes /= 1024

# temporary fix for wrong detection in win 11
def get_release():
    pf = uname()
    ver = pf.version
    if int(ver[5:]) > 22000: 
        return "11"
    return ver

        
dpg.create_context()

with dpg.window(label="PROCESSOR INFORMATION", pos=[50, 100], width=500, height=300, no_close=True):
    dpg.add_text("Name: {0} @ {1} Mhz ".format(cpu.get_name(), cpu_freq().current), bullet=True)
    dpg.add_text("Total Core/s: {0} ".format(cpu.get_core_count()), bullet=True)
    dpg.add_text("Architecture: {0} ".format(cpu.get_arch()), bullet=True)
    with dpg.tree_node(label="Caches "):
        caches = cpu.get_caches()
        dpg.add_text("L1 Data Cache Size: {0}".format(caches[0]), bullet=True)
        dpg.add_text("L1 Instruction Cache Size: {0}".format(caches[1]), bullet=True)
        dpg.add_text("L2 Cache Size: {0}".format(caches[2]), bullet=True)
        dpg.add_text("L2 Cache Line Size: {0}".format(caches[3]), bullet=True)
        dpg.add_text("L2 Cache Associativity: {0}".format(caches[4]), bullet=True)
        dpg.add_text("L3 Cache Size: {0}".format(caches[5]), bullet=True)
    with dpg.tree_node(label="Flags ", default_open=True):
        with dpg.child_window(label="Flags ", autosize_x=True, height=150):
            flags = cpu.get_flags()
            for flag in range(len(flags)):
                dpg.add_text(f"{flags[flag]}", color=GREEN, bullet=True)

with dpg.window(label="MEMORY INFORMATION", pos=[310, 220], width=240, height=210, no_close=True):
    mem = virtual_memory()
    with dpg.tree_node(label="Memory details ", default_open=True):
        dpg.add_text("Used: {0}({1}%)".format(get_size(mem.used), mem.percent), bullet=True)
        dpg.add_text("Available: {0}".format(get_size(mem.available)), bullet=True)
        dpg.add_text("Total: {0}".format(get_size(mem.total)), bullet=True)
    with dpg.tree_node(label="Swap Memory details", default_open=True):
        swap = swap_memory()
        used = swap.used
        percent = swap.percent
        free = swap.free
        total = swap.total

        # check if swap details are available
        if used < 0: used = 0
        if percent < 0.00: percent = 0.0
        if free < 0: free = 0
        if total < 0: total = 0

        dpg.add_text("Used: {0}({1}%)".format(get_size(used), percent), bullet=True)
        dpg.add_text("Free: {0}".format(get_size(free)), bullet=True)
        dpg.add_text("Total: {0}".format(get_size(total)), bullet=True)

with dpg.window(label="DISK INFORMATION", pos=[510, 120], width=630, height=230, no_close=True):
    with dpg.table(label="Disk details ", width=600, height=600, resizable=True, policy=dpg.mvTable_SizingStretchProp,
            borders_outerH=True, borders_innerV=True, borders_innerH=True, borders_outerV=True):
        dpg.add_table_column(label="Device")
        dpg.add_table_column(label="Mountpoint")
        dpg.add_table_column(label="File System type")
        dpg.add_table_column(label="Used")
        dpg.add_table_column(label="Free")
        dpg.add_table_column(label="Total")

        prts = disk_partitions()
        for prt in prts:
            with dpg.table_row():
                for row in range(16):
                    dpg.add_text("{0}".format(prt.device), color=GREEN)
                    dpg.add_text("{0}".format(prt.mountpoint))
                    dpg.add_text("{0}".format(prt.fstype))
                    try: usage = disk_usage(prt.mountpoint)
                    except PermissionError: continue
                    dpg.add_text("{0}({1}%)".format(get_size(usage.used), usage.percent))
                    dpg.add_text("{0}".format(get_size(usage.free)))
                    dpg.add_text("{0}".format(get_size(usage.total)))

with dpg.window(label="NETWORK INFORMATION", pos=[510, 120], width=290, height=230, no_close=True):
    with dpg.tree_node(label="Network Interfaces", default_open=True):
        addrs = net_if_addrs()
        for name, addresses in addrs.items(): 
            dpg.add_text("Name: {0}".format(name))
            for address in addresses:
                if str(address.family) == 'AddressFamily.AF_INET':
                    dpg.add_text("IP Address: {0}".format(address.address), bullet=True)
                    dpg.add_text("Netmask: {0}".format(address.netmask), bullet=True)
                    dpg.add_text("Broadcast IP: {0}".format(address.broadcast), bullet=True)
                elif str(address.family) == 'AddressFamily.AF_LINK':
                    dpg.add_text("MAC Address: {0}".format(address.address), bullet=True)
                    dpg.add_text("Netmask: {0}".format(address.netmask), bullet=True)
                    dpg.add_text("Broadcast MAC: {0}".format(address.broadcast), bullet=True)

with dpg.window(label="OPERATING SYSTEM INFORMATION", pos=[510, 120], width=590, height=230, no_close=True):
    with dpg.tree_node(label="OS details", default_open=True):
        pf = uname()
        dpg.add_text("Computer Name: {0}".format(pf.node), bullet=True)
        dpg.add_text("System: {0}".format(pf.system), bullet=True)
        dpg.add_text("Release: {0}".format(get_release()), bullet=True)
        dpg.add_text("Version: {0}".format(pf.version), bullet=True)
        dpg.add_text("Machine: {0}".format(pf.machine), bullet=True)
        dpg.add_text("Processor: {0}".format(pf.processor), bullet=True)
    
    timepstamp = boot_time()
    bt = datetime.fromtimestamp(timepstamp)
    boot = "{0}/{1}/{2} {3}:{4}:{5}".format(bt.month, bt.day, bt.year, bt.hour, bt.minute, bt.second)
    dpg.add_text(f"Boot Time: {boot}")

with dpg.window(label="GPU INFORMATION", pos=[310, 150], width=280, height=100, no_close=True):
    gpus = gpu.get_name()
    for gpu in gpus:
        dpg.add_text("Name: {0}".format(gpu.decode('utf-8')))

    
dpg.create_viewport(title='SYStem Information Gatherer', small_icon="assets/icon.ico", width=WIN_WIDTH, height=WIN_HEIGHT)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()