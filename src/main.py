from datetime import datetime
import dearpygui.dearpygui as dpg
import cpu
import gpu
import opersys
import helpers
from psutil import *
from platform import uname

cpu = cpu.CPU
gpu = gpu.GPU
opersys = opersys.OPERSYS
helpers = helpers.HELPERS

WIN_WIDTH = 1024
WIN_HEIGHT = 640

RED = [255, 0, 0]
BLUE = [0, 0, 255]
GREEN = [0, 255, 0]

dpg.create_context()
dpg.create_viewport(title='SYSIG | System Information Gatherer', small_icon="res/icon.ico", width=WIN_WIDTH, height=WIN_HEIGHT)
dpg.setup_dearpygui()

with dpg.window(label="PROCESSOR INFORMATION", pos=[0, 0], width=500, height=350, no_close=True):
    dpg.add_text(f"Name: {cpu.get_name()} @ {cpu_freq().current} Mhz ", bullet=True)
    dpg.add_text(f"Total Core/s: {cpu.get_core_count()} ", bullet=True)

    # TODO: do realtime cpu usage output (someone help me :))
    dpg.add_text(f"Total CPU Usage: {cpu_percent(interval=1)}% ", bullet=True)
    with dpg.tree_node(label="CPU Usage(per core): "):
        for core, percentage in enumerate(cpu_percent(interval=1, percpu=True)):
            dpg.add_text(f" Core {core}: {percentage}%", bullet=True)
    dpg.add_text(f"Architecture: {cpu.get_arch()} ", bullet=True)
    with dpg.tree_node(label="Caches "):
        caches = cpu.get_caches()
        dpg.add_text(f"L1 Data Cache Size: {caches[0]}", bullet=True)
        dpg.add_text(f"L1 Instruction Cache Size: {caches[1]}", bullet=True)
        dpg.add_text(f"L2 Cache Size: {caches[2]}", bullet=True)
        dpg.add_text(f"L2 Cache Line Size: {caches[3]}", bullet=True)
        dpg.add_text(f"L2 Cache Associativity: {caches[4]}", bullet=True)
        dpg.add_text(f"L3 Cache Size: {caches[5]}", bullet=True)
    with dpg.tree_node(label="Flags ", default_open=True):
        with dpg.child_window(label="Flags ", autosize_x=True, height=150):
            flags = cpu.get_flags()
            for flag in range(len(flags)):
                dpg.add_text(f"{flags[flag]}", color=GREEN, bullet=True)

with dpg.window(label="MEMORY INFORMATION", pos=[0, 350], width=240, height=210, no_close=True):
    mem = virtual_memory()
    with dpg.tree_node(label="Memory details ", default_open=True):
        dpg.add_text(f"Used: {helpers.get_size(mem.used)}({mem.percent}%)", bullet=True)
        dpg.add_text(f"Available: {helpers.get_size(mem.available)}", bullet=True)
        dpg.add_text(f"Total: {helpers.get_size(mem.total)}", bullet=True)
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

        dpg.add_text(f"Used: {helpers.get_size(used)}({percent}%)", bullet=True)
        dpg.add_text(f"Free: {helpers.get_size(free)}", bullet=True)
        dpg.add_text(f"Total: {helpers.get_size(total)}", bullet=True)

with dpg.window(label="DISK INFORMATION", pos=[500, 0], width=630, height=230, no_close=True):
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
                    dpg.add_text(f"{prt.device}", color=GREEN)
                    dpg.add_text(f"{prt.mountpoint}")
                    dpg.add_text(f"{prt.fstype}")
                    try: usage = disk_usage(prt.mountpoint)
                    except PermissionError: continue
                    dpg.add_text(f"{helpers.get_size(usage.used)}({usage.percent}%)")
                    dpg.add_text(f"{helpers.get_size(usage.free)}")
                    dpg.add_text(f"{helpers.get_size(usage.total)}")

with dpg.window(label="NETWORK INFORMATION", pos=[240, 350], width=290, height=230, no_close=True):
    with dpg.tree_node(label="Network Interfaces", default_open=True):
        addrs = net_if_addrs()
        for name, addresses in addrs.items():
            dpg.add_text(f"Name: {name}")
            for address in addresses:
                if str(address.family) == 'AddressFamily.AF_INET':
                    dpg.add_text(f"IP Address: {address.address}", bullet=True)
                    dpg.add_text(f"Netmask: {address.netmask}", bullet=True)
                    dpg.add_text(f"Broadcast IP: {address.broadcast}", bullet=True)
                elif str(address.family) == 'AddressFamily.AF_LINK':
                    dpg.add_text(f"MAC Address: {address.address}", bullet=True)
                    dpg.add_text(f"Netmask: {address.netmask}", bullet=True)
                    dpg.add_text(f"Broadcast MAC: {address.broadcast}", bullet=True)

with dpg.window(label="OPERATING SYSTEM INFORMATION", pos=[530, 230], width=590, height=230, no_close=True):
    with dpg.tree_node(label="OS details", default_open=True):
        pf = uname()
        dpg.add_text(f"Computer Name: {pf.node}", bullet=True)
        dpg.add_text(f"System: {pf.system}", bullet=True)
        dpg.add_text(f"Release: {opersys.get_release()}", bullet=True)
        dpg.add_text(f"Version: {pf.version}", bullet=True)
        dpg.add_text(f"Machine: {pf.machine}", bullet=True)
        dpg.add_text(f"Processor: {pf.processor}", bullet=True)
    
    timestamp = boot_time()
    bt = datetime.fromtimestamp(timestamp)
    boot = bt.strftime("%m/%d/%Y %H:%M:%S")
    dpg.add_text(f"Boot Time: {boot}")

with dpg.window(label="GPU INFORMATION", pos=[530, 460], width=280, height=100, no_close=True):
    gpus = gpu.get_name()
    for gpu in gpus:
        dpg.add_text(f"Name: {gpu.decode('utf-8')}")

dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()