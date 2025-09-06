import os
import psutil
import time
from win10toast import ToastNotifier
import pystray
from PIL import Image

# Debug: show working dir and icon presence
print("CWD:", os.getcwd(), "| icon.ico exists?", os.path.exists('icon.ico'))

# Initialize toaster
toaster = ToastNotifier()

# Menu callbacks
def show_cpu_ram(icon, item):
    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory().percent
    toaster.show_toast('CPU & RAM Usage', f'CPU: {cpu}%\nRAM: {ram}%', duration=5)

def show_disk(icon, item):
    disk = psutil.disk_usage('/').percent
    toaster.show_toast('Disk Usage', f'Disk: {disk}%', duration=5)

def quit_app(icon, item):
    icon.stop()

# Load your .ico file
icon_image = Image.open('icon.ico')

# Build menu
menu = (
    pystray.MenuItem('Show CPU & RAM', show_cpu_ram),
    pystray.MenuItem('Show Disk Usage', show_disk),
    pystray.MenuItem('Exit', quit_app)
)

# Create and run the tray icon
tray_icon = pystray.Icon('TrayMonitor', icon_image, 'TrayMonitor', pystray.Menu(*menu))
tray_icon.run()