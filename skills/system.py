
import os
import datetime
import platform
import psutil
from command_registry import registry

@registry.register(name="get_time", description="Returns current date and time.", safe=True)
def get_time():
    """Returns the current system time."""
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

@registry.register(name="system_info", description="Get CPU, RAM, and OS info.", safe=True)
def system_info():
    """Returns system diagnostic information."""
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    os_info = f"{platform.system()} {platform.release()}"
    return f"OS: {os_info} | CPU Usage: {cpu}% | RAM Usage: {ram}%"

@registry.register(name="shutdown_system", description="Shuts down the computer.", safe=False)
def shutdown_system(delay: int = 60):
    """Schedules a system shutdown."""
    # This requires confirmation via the registry flag
    if platform.system() == "Windows":
        os.system(f"shutdown /s /t {delay}")
    else:
        os.system(f"shutdown -h +{delay//60}")
    return f"Shutdown scheduled in {delay} seconds."
