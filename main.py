 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/main.py b/main.py
index 780c48b8583fa75989a4d5a33cef0674df83f401..07076e3dcd8cf4e96be04bd924e05a423565e6de 100644
--- a/main.py
+++ b/main.py
@@ -1,39 +1,71 @@
 import os
+import platform
 import psutil
-import time
 from win10toast import ToastNotifier
 import pystray
 from PIL import Image
 
-# Debug: show working dir and icon presence
-print("CWD:", os.getcwd(), "| icon.ico exists?", os.path.exists('icon.ico'))
 
-# Initialize toaster
-toaster = ToastNotifier()
+def get_icon_path() -> str:
+    """Return the absolute icon path next to this script."""
+    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico")
 
-# Menu callbacks
-def show_cpu_ram(icon, item):
+
+def get_root_disk_path() -> str:
+    """Return a platform-appropriate root path for disk usage checks."""
+    if os.name == "nt":
+        system_drive = os.environ.get("SystemDrive", "C:")
+        return f"{system_drive}\\"
+    return "/"
+
+
+def show_notification(toaster: ToastNotifier, title: str, message: str):
+    """Show a toast notification without crashing the tray app on failure."""
+    try:
+        toaster.show_toast(title, message, duration=5)
+    except Exception as exc:
+        print(f"Notification error: {exc}")
+
+
+def show_cpu_ram(icon, item, toaster: ToastNotifier):
     cpu = psutil.cpu_percent(interval=0.5)
     ram = psutil.virtual_memory().percent
-    toaster.show_toast('CPU & RAM Usage', f'CPU: {cpu}%\nRAM: {ram}%', duration=5)
+    show_notification(toaster, "CPU & RAM Usage", f"CPU: {cpu}%\nRAM: {ram}%")
+
+
+def show_disk(icon, item, toaster: ToastNotifier):
+    disk_path = get_root_disk_path()
+    disk = psutil.disk_usage(disk_path).percent
+    show_notification(toaster, "Disk Usage", f"{disk_path} usage: {disk}%")
 
-def show_disk(icon, item):
-    disk = psutil.disk_usage('/').percent
-    toaster.show_toast('Disk Usage', f'Disk: {disk}%', duration=5)
 
 def quit_app(icon, item):
     icon.stop()
 
-# Load your .ico file
-icon_image = Image.open('icon.ico')
 
-# Build menu
-menu = (
-    pystray.MenuItem('Show CPU & RAM', show_cpu_ram),
-    pystray.MenuItem('Show Disk Usage', show_disk),
-    pystray.MenuItem('Exit', quit_app)
-)
+def load_icon() -> Image.Image:
+    icon_path = get_icon_path()
+    if os.path.exists(icon_path):
+        return Image.open(icon_path)
+
+    print(f"Warning: icon not found at {icon_path}. Using fallback icon.")
+    return Image.new("RGBA", (64, 64), (35, 35, 35, 255))
+
+
+def main():
+    toaster = ToastNotifier()
+    icon_image = load_icon()
+
+    menu = (
+        pystray.MenuItem("Show CPU & RAM", lambda i, it: show_cpu_ram(i, it, toaster)),
+        pystray.MenuItem("Show Disk Usage", lambda i, it: show_disk(i, it, toaster)),
+        pystray.MenuItem("Exit", quit_app),
+    )
+
+    title = f"TrayMonitor ({platform.system()})"
+    tray_icon = pystray.Icon("TrayMonitor", icon_image, title, pystray.Menu(*menu))
+    tray_icon.run()
+
 
-# Create and run the tray icon
-tray_icon = pystray.Icon('TrayMonitor', icon_image, 'TrayMonitor', pystray.Menu(*menu))
-tray_icon.run()
\ No newline at end of file
+if __name__ == "__main__":
+    main()
 
EOF
)
