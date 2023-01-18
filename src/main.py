from datetime import datetime
import dearpygui.dearpygui as dpg
import cpu
import gpu
import opersys
import helpers
import psutil
from platform import uname
import socket

WIN_WIDTH = 1024
WIN_HEIGHT = 640

RED = [255, 0, 0]
BLUE = [0, 0, 255]
GREEN = [0, 255, 0]

dpg.create_context()
dpg.create_viewport(title='SYSIG | System Information Gatherer',
                    small_icon="res/icon.ico",
                    x_pos=0, y_pos=0, width=WIN_WIDTH, height=WIN_HEIGHT)

dpg.setup_dearpygui()

with dpg.window(label="PROCESSOR INFORMATION", pos=[0, 0], width=500, height=350, no_close=True):
    dpg.add_text(f"Name: {cpu.get_name()} @ {psutil.cpu_freq().current} Mhz ", bullet=True)
    dpg.add_text(f"Total Core/s: {cpu.get_core_count()} ", bullet=True)

    # TODO: do realtime cpu usage output (someone help me :))
    dpg.add_text(f"Total CPU Usage: {psutil.cpu_percent(interval=1)}% ", bullet=True)
    with dpg.tree_node(label="CPU Usage(per core): "):
        for core, percentage in enumerate(psutil.cpu_percent(interval=1, percpu=True)):
            dpg.add_text(f" Core {core}: {percentage}%", bullet=True)
    dpg.add_text(f"Architecture: {cpu.get_arch()} ", bullet=True)
    with dpg.tree_node(label="Caches "):
        caches = cpu.get_caches()
        dpg.add_text(f"L1 Data Cache Size: {caches[0]}", bullet=True)
        dpg.add_text(f"L1 Instruction Cache Size: {caches[1]}", bullet=True)
        dpg.add_text(f"L2 Cache Size: {caches[2]}", bullet=True)
        dpg.add_text(f"L3 Cache Size: {caches[3]}", bullet=True)
    with dpg.tree_node(label="Flags ", default_open=True):
        with dpg.table(header_row=False, policy=dpg.mvTable_SizingStretchProp,
                       borders_outerV=True, borders_innerV=True,
                       resizable=True, borders_outerH=True, borders_innerH=True):
            COL = 11
            idx = 0
            flags = cpu.get_flags()

            for _ in range(COL):
                dpg.add_table_column()

            # credit from @Sikwate: https://github.com/hoffstadt/DearPyGui/discussions/1918#discussioncomment-3960795
            # improved by @diamant3
            rows = int(len(flags) / COL) + 1
            for row in range(rows):
                with dpg.table_row():
                    for col in range(COL):
                        idx = row * COL + col
                        if idx >= len(flags):
                            dpg.add_text("Empty")
                        else:
                            dpg.add_text(f"{flags[idx]}", color=GREEN)

with dpg.window(label="MEMORY INFORMATION", pos=[0, 350], width=240, height=210, no_close=True):
    mem = psutil.virtual_memory()
    with dpg.tree_node(label="Memory details ", default_open=True):
        dpg.add_text(f"Used: {helpers.get_size(mem.used)}({mem.percent}%)", bullet=True)
        dpg.add_text(f"Available: {helpers.get_size(mem.available)}", bullet=True)
        dpg.add_text(f"Total: {helpers.get_size(mem.total)}", bullet=True)
    with dpg.tree_node(label="Swap Memory details", default_open=True):
        swap = psutil.swap_memory()

        dpg.add_text(f"Used: {helpers.get_size(swap.used)}({swap.percent}%)", bullet=True)
        dpg.add_text(f"Free: {helpers.get_size(swap.free)}", bullet=True)
        dpg.add_text(f"Total: {helpers.get_size(swap.total)}", bullet=True)

with dpg.window(label="DISK INFORMATION", pos=[500, 0], width=630, height=230, no_close=True):
    with dpg.table(label="Disk details ", resizable=True, policy=dpg.mvTable_SizingStretchProp,
                   borders_outerV=True, borders_innerV=True,
                   borders_outerH=True, borders_innerH=True):
        dpg.add_table_column(label="Device")
        dpg.add_table_column(label="Mountpoint")
        dpg.add_table_column(label="File System type")
        dpg.add_table_column(label="Used")
        dpg.add_table_column(label="Free")
        dpg.add_table_column(label="Total")

        prts = psutil.disk_partitions()
        for prt in prts:
            with dpg.table_row():
                for row in range(16):
                    dpg.add_text(f"{prt.device}", color=GREEN)
                    dpg.add_text(f"{prt.mountpoint}")
                    dpg.add_text(f"{prt.fstype}")
                    try:
                        usage = psutil.disk_usage(prt.mountpoint)
                    except PermissionError:
                        continue
                    dpg.add_text(f"{helpers.get_size(usage.used)}({usage.percent}%)")
                    dpg.add_text(f"{helpers.get_size(usage.free)}")
                    dpg.add_text(f"{helpers.get_size(usage.total)}")

with dpg.window(label="NETWORK INFORMATION", pos=[240, 350], width=290, height=230, no_close=True):
    with dpg.tree_node(label="Network Interfaces", default_open=True):
        addrs = psutil.net_if_addrs()
        for name, addresses in addrs.items():
            dpg.add_text(f"Name: {name}")
            for address in addresses:
                if address.family == socket.AF_INET:
                    dpg.add_text(f"IP Address: {address.address}", bullet=True)
                    dpg.add_text(f"Netmask: {address.netmask}", bullet=True)
                    dpg.add_text(f"Broadcast IP: {address.broadcast}", bullet=True)
                if address.family == psutil.AF_LINK:
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

    timestamp = psutil.boot_time()
    bt = datetime.fromtimestamp(timestamp)
    boot = bt.strftime("%m/%d/%Y %I:%M:%S %p")
    dpg.add_text(f"Last boot timestamp: {boot}")

with dpg.window(label="GPU INFORMATION", pos=[530, 460], width=280, height=100, no_close=True):
    gpus = gpu.get_name()
    for gfx in gpus:
        dpg.add_text(f"Name: {gfx.decode('utf-8')}")

with dpg.theme() as global_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 6, category=dpg.mvThemeCat_Core)

dpg.bind_theme(global_theme)
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
