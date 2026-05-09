import os
import platform
import time

import psutil

from ValentinMusic.misc import _boot_
from ValentinMusic.utils.formatters import get_readable_time


async def bot_sys_stats():
    bot_uptime = int(time.time() - _boot_)
    UP = f"{get_readable_time(bot_uptime)}"
    CPU = f"{psutil.cpu_percent(interval=0.5)}%"
    RAM = f"{psutil.virtual_memory().percent}%"

    # Use appropriate disk path based on OS
    if platform.system() == "Windows":
        disk_path = os.getenv("SystemDrive", "C:") + "\\"
    else:
        disk_path = "/"

    DISK = f"{psutil.disk_usage(disk_path).percent}%"
    return UP, CPU, RAM, DISK
