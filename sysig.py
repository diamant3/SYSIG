"""
    SYSIG - System Information Gatherer

    Simple GUI tool to gather system information in your computer
"""

from datetime import datetime

import platform
import socket
import threading
import subprocess
import GPUtil
import psutil
import humanize
import wmi
import subprocess, re
AMD_SUPPORTED = False
try:
    import pyadl
    
    # Just a dummy call to check if AMD driver can be accessed.
    # If the driver isn't found, it should raise the ADLError.
    _ = pyadl.ADLManager.getInstance().getDevices()
    
    AMD_SUPPORTED = True
except (ImportError, Exception):
    pass


import dearpygui.dearpygui as dpg
from cpuinfo import get_cpu_info

gci = get_cpu_info()
WIN_WIDTH = 800
WIN_HEIGHT = 400

dpg.create_context()


# Get CPU Total Utilization
def get_cpu_util():
    """Get CPU Total Utilization"""

    while True:
        cpu_val = psutil.cpu_percent(interval=1, percpu=False)
        dpg.set_value(cpu_progress_bar, 1.0 / 100.0 * cpu_val)
        dpg.configure_item(cpu_progress_bar, overlay=f"{cpu_val}%")


# entry
with dpg.window(
        label=f"Computer Name: {platform.node()}",
        no_close=True,
        no_resize=True,
        no_move=True,
        width=WIN_WIDTH - 18,
        height=WIN_HEIGHT
) as main_window:
    with dpg.collapsing_header(label="Processor"):
        with dpg.group(horizontal=True):
            dpg.add_text(f"{gci['brand_raw']} @", bullet=True)
            dpg.add_text(f"{gci['hz_actual_friendly']}")
        with dpg.group(horizontal=True):
            dpg.add_text("CPU Utilization(Total):", bullet=True)
            threading.Thread(target=get_cpu_util, args=(), daemon=True).start()
            cpu_progress_bar = dpg.add_progress_bar(default_value=0.0, overlay="0.0%", width=200)
        dpg.add_text(f"{gci['count']} Total Core/s", bullet=True)
        dpg.add_text(f"{gci['arch']} Architecture", bullet=True)
        with dpg.tree_node(label="Cache/s"):
            try:
                l1_i = humanize.naturalsize(gci['l1_instruction_cache_size'], gnu=True)
                dpg.add_text(f"L1 Instruction Cache Size: {l1_i}")
            except KeyError:
                dpg.add_text("L1 Instruction Cache Size: Can't determine")

            try:
                l1_d = humanize.naturalsize(gci['l1_data_cache_size'], gnu=True)
                dpg.add_text(f"L1 Data Cache Size: {l1_d}")
            except KeyError:
                dpg.add_text("L1 Data Cache Size: Can't determine")

            try:
                l2 = humanize.naturalsize(gci['l2_cache_size'], gnu=True)
                dpg.add_text(f"L2 Cache Size: {l2}")
            except KeyError:
                dpg.add_text("L2 Cache Size: Can't determine")

            try:
                l3 = humanize.naturalsize(gci['l3_cache_size'], gnu=True)
                dpg.add_text(f"L3 Cache Size: {l3}")
            except KeyError:
                dpg.add_text("L3 Cache Size: Can't determine")

        with dpg.tree_node(label="Flags"):
            with dpg.table(
                header_row=False,
                resizable=True,
                policy=dpg.mvTable_SizingStretchProp,
                row_background=True,
                borders_outerV=True,
                borders_innerV=True,
                borders_outerH=True,
                borders_innerH=True,
                delay_search=True
            ):
                COL = 11
                FLAG = 0
                flags = gci['flags']

                for _ in range(COL):
                    dpg.add_table_column()

                # https://github.com/hoffstadt/DearPyGui/discussions/1918#discussioncomment-3960795
                rows = int(len(flags) / COL) + 1
                for row in range(rows):
                    with dpg.table_row():
                        for col in range(COL):
                            FLAG = row * COL + col
                            if FLAG >= len(flags):
                                dpg.add_text("---")
                            else:
                                dpg.add_text(f"{flags[FLAG]}")

    with dpg.collapsing_header(label="Graphics"):
        gpu_list = []

        # amd
        if AMD_SUPPORTED:
            try:
                amd = pyadl.ADLManager.getInstance().getDevices()
                for gpu in amd:
                    gpu_list.append(gpu.adapterName)
            except:
                dpg.add_text("Could not fetch AMD graphics information.", bullet=True)
        else:
            # nvidia
            nvidia = GPUtil.getGPUs()
            for gpu in nvidia:
                gpu_list.append(gpu.name)

            for gfx in gpu_list:
                dpg.add_text(f"Graphics Name: {gfx}", bullet=True)

    with dpg.collapsing_header(label="Memory"):
        mem = psutil.virtual_memory()
        mem_used = humanize.naturalsize(mem.used)
        mem_percent = mem.percent
        mem_avail = humanize.naturalsize(mem.available)
        mem_total = humanize.naturalsize(mem.total)
        dpg.add_text("MAIN MEMORY", color=(0, 255, 0))
        dpg.add_text(f"Used Memory: {mem_used}({mem_percent}%)", bullet=True)
        dpg.add_text(f"Available Memory: {mem_avail}", bullet=True)
        dpg.add_text(f"Total Memory: {mem_total}", bullet=True)

        swap = psutil.swap_memory()
        swap_used = humanize.naturalsize(swap.used)
        swap_percent = swap.percent
        swap_free = humanize.naturalsize(swap.free)
        swap_total = humanize.naturalsize(swap.total)
        dpg.add_text("SWAP MEMORY", color=(0, 255, 0))
        dpg.add_text(f"Used Swap Memory: {swap_used}({swap_percent}%)", bullet=True)
        dpg.add_text(f"Free Swap Memory: {swap_free}", bullet=True)
        dpg.add_text(f"Total Swap Memory: {swap_total}", bullet=True)
        
    with dpg.collapsing_header(label="Temperature"):
        def get_cpu_temperature():
            if platform.system() == 'Windows':
                try:
                    import wmi
                    w = wmi.WMI(namespace="root\wmi")
                    temperature_info = w.MSAcpi_ThermalZoneTemperature()[0]
                    return temperature_info.CurrentTemperature / 10.0 - 273.15
                except wmi.x_access_denied:
                    return "Access Denied (Run script as administrator)"
                except Exception as e:
                    return f"Error: {e}"
            elif platform.system() == 'Linux':
                temp = psutil.sensors_temperatures()
                if 'coretemp' in temp:  # Typically for Intel and some AMD CPUs on Linux
                    for item in temp['coretemp']:
                        if item.label == 'Package id 0':  # Overall CPU temperature
                            return item.current
                elif 'Tdie' in temp:  # Typically for AMD processors
                    return temp['Tdie'][0].current
            elif platform.system() == 'Darwin':  # macOS
                temp = psutil.sensors_temperatures()
                if 'TC0D' in temp:
                    return temp['TC0D'][0].current

            return None

        cpu_temp = get_cpu_temperature()
        if cpu_temp:
            dpg.add_text(f"CPU Temperature: {cpu_temp}°C", bullet=True)
        else:
            dpg.add_text("CPU Temperature: Not Available", bullet=True)

        # NVIDIA GPU temperature
        try:
            gpus = GPUtil.getGPUs()
            for gpu in gpus:
                dpg.add_text(f"NVIDIA GPU {gpu.id} ({gpu.name}) Temperature: {gpu.temperature}°C", bullet=True)
        except (ImportError, Exception) as e:
            dpg.add_text(f"Error fetching NVIDIA GPU temperature: {e}", bullet=True)
        
        # AMD GPU temperature (using pyadl)
        if AMD_SUPPORTED:
            try:
                amd_manager = pyadl.ADLManager.getInstance()
                devices = amd_manager.getDevices()
                for device in devices:
                    temperature_data = device.getTemperature()
                    if temperature_data is not None:
                        dpg.add_text(f"AMD GPU {device.adapterName} Temperature: {temperature_data}°C", bullet=True)
            except Exception as e:
                dpg.add_text(f"Error fetching AMD GPU temperature: {e}", bullet=True)

    with dpg.collapsing_header(label="Disk"):
        with dpg.table(
            resizable=True,
            policy=dpg.mvTable_SizingStretchProp,
            borders_outerV=True,
            borders_innerV=True,
            borders_outerH=True,
            borders_innerH=True,
            delay_search=True
        ):
            dpg.add_table_column(label="Device")
            dpg.add_table_column(label="Mount point")
            dpg.add_table_column(label="File System type")
            dpg.add_table_column(label="Used")
            dpg.add_table_column(label="Free")
            dpg.add_table_column(label="Total")

            prts = psutil.disk_partitions()
            for prt in prts:
                with dpg.table_row():
                    for row in range(8):
                        dpg.add_text(f"{prt.device}", color=(0, 255, 0))
                        dpg.add_text(f"{prt.mountpoint}")
                        dpg.add_text(f"{prt.fstype}")
                        try:
                            usage = psutil.disk_usage(prt.mountpoint)
                        except PermissionError:
                            dpg.add_text("Can't determine")
                            continue
                        dpg.add_text(f"{humanize.naturalsize(usage.used)}({usage.percent}%)")
                        dpg.add_text(f"{humanize.naturalsize(usage.free)}")
                        dpg.add_text(f"{humanize.naturalsize(usage.total)}")
                        

    with dpg.collapsing_header(label="Network"):
        addr_list = psutil.net_if_addrs()
        for name, addresses in addr_list.items():
            with dpg.group(horizontal=True):
                dpg.add_text("Interface Name: ")
                dpg.add_text(f"{name}", color=(0, 255, 0))
            for address in addresses:
                if address.family == socket.AF_INET:
                    dpg.add_text(f"IP Address: {address.address}", bullet=True)
                    dpg.add_text(f"Subnet Mask: {address.netmask}", bullet=True)
                if address.family == psutil.AF_LINK:
                    dpg.add_text(f"MAC Address: {address.address}", bullet=True)

    with dpg.collapsing_header(label="Operating System"):
        if platform.system() == 'Windows':
            try:
                BRAND = subprocess.check_output('wmic csproduct get vendor', shell=True)
                BRAND = BRAND.decode('utf-8').strip().split('\n')[1]
                MODEL = subprocess.check_output('wmic csproduct get name', shell=True)
                MODEL = MODEL.decode('utf-8').strip().split('\n')[1]

                dpg.add_text(f"Brand: {BRAND}", bullet=True)
                dpg.add_text(f"Model: {MODEL}", bullet=True)
            except subprocess.CalledProcessError:
                dpg.add_text("Brand: Can't determine", bullet=True)
                dpg.add_text("Model: Can't determine", bullet=True)

        elif platform.system() == 'Linux':
            try:
                BRAND = subprocess.check_output('dmidecode -s system-manufacturer', shell=True)
                BRAND = BRAND.decode('utf-8').strip()
                MODEL = subprocess.check_output('dmidecode -s system-product-name', shell=True)
                MODEL = MODEL.decode('utf-8').strip()

                dpg.add_text(f"Brand: {BRAND}", bullet=True)
                dpg.add_text(f"Model: {MODEL}", bullet=True)
            except subprocess.CalledProcessError:
                dpg.add_text("Brand: Can't determine", bullet=True)
                dpg.add_text("Model: Can't determine", bullet=True)

        uname = platform.uname()
        dpg.add_text(f"System: {uname.system}", bullet=True)
        if uname.system == "Windows":
            if int(uname.version[5:]) > 22000:
                dpg.add_text("Version: 11", bullet=True)
        dpg.add_text(f"Machine: {uname.machine}", bullet=True)

        timestamp = psutil.boot_time()
        bt = datetime.fromtimestamp(timestamp)
        boot = bt.strftime("%m/%d/%Y %I:%M:%S %p")
        dpg.add_text(f"Last boot timestamp: {boot}", bullet=True)

dpg.create_viewport(
    title="System Information Gatherer",
    small_icon="res/icon.ico",
    large_icon="res/icon.ico",
    resizable=False,
    max_width=WIN_WIDTH,
    max_height=WIN_HEIGHT
)
dpg.setup_dearpygui()
dpg.set_primary_window(main_window, True)
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
