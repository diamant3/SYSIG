"""
    SYSIG - System Information Gatherer
"""

import threading
import socket
import platform
import subprocess
import os
from datetime import datetime

import dearpygui.dearpygui as dpg

from cpuinfo import get_cpu_info

import humanize
import psutil

if platform.system() == 'Windows':
    import winreg

AMD_SUPPORTED = False
NVIDIA_SUPPORTED = False
try:
    import pyadl
    import GPUtil
    if len(pyadl.ADLManager.getInstance().getDevices()) > 0:
        AMD_SUPPORTED = True

    if len(GPUtil.getGPUs()) > 0:
        NVIDIA_SUPPORTED = True
except ImportError:
    pass

WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
COLOR = (0, 255, 54)
ICON = os.getcwd() + "/resource/icon.ico"

GCI = get_cpu_info()

dpg.create_context()
dpg.create_viewport(
    title="SYSIG",
    small_icon=ICON,
    large_icon=ICON,
    width=WINDOW_WIDTH,
    max_width=WINDOW_WIDTH,
    height=WINDOW_HEIGHT,
    max_height=WINDOW_HEIGHT,
    clear_color=(18, 18, 18)
)
dpg.setup_dearpygui()

# Main window
with dpg.window(
        no_title_bar=True,
        no_move=True,
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT,
        pos=(0, 0),
    ):
    dpg.add_text("System Information Gatherer", pos=(int(WINDOW_WIDTH / 2.9), 12), color=COLOR)

    dpg.add_button(
        label="Processor Information",
        width=256,
        height=32,
        pos=(int(WINDOW_WIDTH / 3.5), 48),
        callback=lambda: dpg.configure_item("Processor_modal_ID", show=True),
    )

    with dpg.window(
        label="Processor Information",
        modal=True,
        show=False,
        tag="Processor_modal_ID",
        autosize=True,
    ):

        freq = humanize.naturalsize(GCI['hz_actual_friendly'], gnu=True)
        dpg.add_text(f"Processor Name: {GCI['brand_raw']} @ {freq}", bullet=True)
        dpg.add_text(f"Processor Count: {GCI['count']}", bullet=True)
        dpg.add_text(f"Architecture: {GCI['arch']}", bullet=True)

        with dpg.tree_node(label="Processor Caches"):
            try:
                l1_data = humanize.naturalsize(GCI['l1_instruction_cache_size'], gnu=True)
                dpg.add_text(f"L1 Instruction Cache Size: {l1_data}", bullet=True)
            except KeyError:
                dpg.add_text("L1 Instruction Cache Size: Can't determine", bullet=True)

            try:
                l1_instruction = humanize.naturalsize(GCI['l1_data_cache_size'],  gnu=True)
                dpg.add_text(f"L1 Data Cache Size: {l1_instruction}", bullet=True)
            except KeyError:
                dpg.add_text("L1 Data Cache Size: Can't determine", bullet=True)

            try:
                l2 = humanize.naturalsize(GCI['l2_cache_size'],  gnu=True)
                dpg.add_text(f"L2 Cache Size: {l2}", bullet=True)
            except KeyError:
                dpg.add_text("L2 Cache Size: Can't determine", bullet=True)

            try:
                l3 = humanize.naturalsize(GCI['l3_cache_size'],  gnu=True)
                dpg.add_text(f"L3 Cache Size: {l3}", bullet=True)
            except KeyError:
                dpg.add_text("L3 Cache Size: Can't determine", bullet=True)

        with dpg.tree_node(label="Flags"):
            with dpg.table(
                header_row=False,
                policy=dpg.mvTable_SizingStretchProp,
                row_background=True,
                borders_innerH=True,
                borders_innerV=True,
            ):
                COL = 8
                FLAG = 0
                flags = GCI['flags']

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

        with dpg.group(horizontal=True):
            dpg.add_text("CPU Utilization(Total): ", bullet=True)

            def cpu_util():
                """ cpu utilization thread """
                while 1:
                    val = psutil.cpu_percent(interval=1, percpu=False)
                    dpg.set_value("util_progress", (1.0 / 100.0) * val)
                    dpg.configure_item("util_progress", overlay=f"{val}%")
            threading.Thread(target=cpu_util, args=(), daemon=True).start()
            dpg.add_progress_bar(tag="util_progress", overlay="0.0%", height=16,)

    dpg.add_button(
        label="Graphics Information",
        width=256,
        height=32,
        pos=(int(WINDOW_WIDTH / 3.5), 96),
        callback=lambda: dpg.configure_item("Graphics_modal_ID", show=True),
    )

    # GPU Temperature detection is unsupported
    with dpg.window(
        label="Graphics Information",
        modal=True,
        show=False,
        tag="Graphics_modal_ID",
        autosize=True,
    ):
        gpu_devices = []
        with dpg.group(horizontal=True):
            if AMD_SUPPORTED:
                devices = pyadl.ADLManager.getInstance().getDevices()
                for device in devices:
                    gpu_devices.append(device.adapterName.decode('utf-8'))

            if NVIDIA_SUPPORTED:
                devices = GPUtil.getGPUs()
                for device in devices:
                    gpu_devices.append(device.gpu_name)
            dpg.add_text(f"Graphics Card: {gpu_devices}", bullet=True)

    dpg.add_button(
        label="Memory Information",
        width=256,
        height=32,
        pos=(int(WINDOW_WIDTH / 3.5), 144),
        callback=lambda: dpg.configure_item("Memory_modal_ID", show=True),
    )

    with dpg.window(
        label="Memory Information",
        modal=True,
        show=False,
        tag="Memory_modal_ID",
        autosize=True,
    ):
        mem = psutil.virtual_memory()
        mem_used = humanize.naturalsize(mem.used)
        mem_percent = mem.percent
        mem_avail = humanize.naturalsize(mem.available)
        mem_total = humanize.naturalsize(mem.total)
        dpg.add_text("MAIN MEMORY")
        dpg.add_text(f"Used Memory: {mem_used}({mem_percent}%)", bullet=True)
        dpg.add_text(f"Available Memory: {mem_avail}", bullet=True)
        dpg.add_text(f"Total Memory: {mem_total}", bullet=True)

        swap = psutil.swap_memory()
        swap_used = humanize.naturalsize(swap.used)
        swap_percent = swap.percent
        swap_free = humanize.naturalsize(swap.free)
        swap_total = humanize.naturalsize(swap.total)
        dpg.add_text("SWAP MEMORY")
        dpg.add_text(f"Used Swap Memory: {swap_used}({swap_percent}%)", bullet=True)
        dpg.add_text(f"Free Swap Memory: {swap_free}", bullet=True)
        dpg.add_text(f"Total Swap Memory: {swap_total}", bullet=True)

    dpg.add_button(
        label="Disk Information",
        width=256,
        height=32,
        pos=(int(WINDOW_WIDTH / 3.5), 192),
        callback=lambda: dpg.configure_item("Disk_modal_ID", show=True,)
    )

    with dpg.window(
        label="Disk Information",
        modal=True,
        show=False,
        tag="Disk_modal_ID",
        autosize=True,
    ):
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

    dpg.add_button(
        label="Network Information",
        width=256,
        height=32,
        pos=(int(WINDOW_WIDTH / 3.5), 240),
        callback=lambda: dpg.configure_item("Network_modal_ID", show=True,)
    )

    with dpg.window(
        label="Network Information",
        modal=True,
        show=False,
        tag="Network_modal_ID",
        autosize=True,
    ):
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

    dpg.add_button(
        label="OS Information",
        width=256,
        height=32,
        pos=(int(WINDOW_WIDTH / 3.5), 288),
        callback=lambda: dpg.configure_item("OS_modal_ID", show=True,)
    )

    with dpg.window(
        label="OS Information",
        modal=True,
        show=False,
        tag="OS_modal_ID",
        autosize=True,
    ):
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

        if platform.system() == "Windows":
            with dpg.tree_node(label="BIOS"):
                bios = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"HARDWARE\DESCRIPTION\System\BIOS"
                )
                vendor = winreg.QueryValueEx(bios, "BIOSVendor")
                version = winreg.QueryValueEx(bios, "BIOSVersion")

                dpg.add_text(f"Vendor: {vendor[0]}", bullet=True)
                dpg.add_text(f"Version: {version[0]}", bullet=True)

    dpg.add_button(
        label="About SYSIG",
        width=256,
        height=32,
        pos=(int(WINDOW_WIDTH / 3.5), 384),
        callback=lambda: dpg.configure_item("About_modal_ID", show=True,)
    )

    with dpg.window(
        label="About SYSIG",
        modal=True,
        show=False,
        tag="About_modal_ID",
        autosize=True,
    ):
        dpg.add_text("SYSIG - System Information Gatherer")
        dpg.add_text("Simple application to gather your system information in your computer.")
        dpg.add_text("")
        dpg.add_text("GitHub Repo: https://github.com/diamant3/SYSIG")
        dpg.add_text("E-Mail: diamant3@proton.me")

dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
