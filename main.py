from __future__ import annotations

import logging
import os
import platform
from functools import partial
from pathlib import Path

import psutil
import pystray
from PIL import Image, ImageDraw
from win10toast import ToastNotifier

APP_NAME = "TrayMonitor"
ICON_SIZE = 64

logger = logging.getLogger(APP_NAME)


def configure_logging() -> None:
    """Configure simple console logging for diagnostics."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def get_icon_path() -> Path:
    """Return the icon path next to this script."""
    return Path(__file__).resolve().parent / "icon.ico"


def get_root_disk_path() -> str:
    """Return a platform-appropriate root path for disk usage checks."""
    if os.name == "nt":
        drive = os.environ.get("SystemDrive", "C:")
        return f"{drive}\\"
    return "/"


def show_notification(toaster: ToastNotifier, title: str, message: str) -> None:
    """Display a toast notification and log failures without crashing."""
    try:
        toaster.show_toast(title, message, duration=5, threaded=True)
    except Exception:
        logger.exception("Failed to show notification: %s", title)


def show_cpu_ram(_icon: pystray.Icon, _item: pystray.MenuItem, toaster: ToastNotifier) -> None:
    """Show current CPU and RAM usage in a toast."""
    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory().percent
    show_notification(toaster, "CPU & RAM Usage", f"CPU: {cpu:.1f}%\nRAM: {ram:.1f}%")


def show_disk(_icon: pystray.Icon, _item: pystray.MenuItem, toaster: ToastNotifier) -> None:
    """Show current root disk usage in a toast."""
    disk_path = get_root_disk_path()
    disk = psutil.disk_usage(disk_path).percent
    show_notification(toaster, "Disk Usage", f"{disk_path} usage: {disk:.1f}%")


def quit_app(icon: pystray.Icon, _item: pystray.MenuItem) -> None:
    """Stop the tray icon event loop."""
    logger.info("Exiting tray application.")
    icon.stop()


def create_fallback_icon(size: int = ICON_SIZE) -> Image.Image:
    """Create a simple fallback icon if icon.ico is unavailable."""
    image = Image.new("RGBA", (size, size), (34, 40, 49, 255))
    draw = ImageDraw.Draw(image)
    margin = size // 6
    draw.rectangle((margin, margin, size - margin, size - margin), outline=(102, 153, 255, 255), width=3)
    draw.line((margin + 4, size - margin - 8, size // 2, size // 2), fill=(102, 255, 153, 255), width=3)
    draw.line((size // 2, size // 2, size - margin - 4, margin + 8), fill=(102, 255, 153, 255), width=3)
    return image


def load_icon() -> Image.Image:
    """Load icon from disk, falling back to generated icon if needed."""
    icon_path = get_icon_path()
    try:
        if icon_path.exists():
            return Image.open(icon_path)
        logger.warning("Icon not found at %s; using fallback icon.", icon_path)
    except OSError:
        logger.exception("Unable to open icon at %s; using fallback icon.", icon_path)

    return create_fallback_icon()


def build_menu(toaster: ToastNotifier) -> pystray.Menu:
    """Build tray context menu with bound callbacks."""
    return pystray.Menu(
        pystray.MenuItem("Show CPU & RAM", partial(show_cpu_ram, toaster=toaster)),
        pystray.MenuItem("Show Disk Usage", partial(show_disk, toaster=toaster)),
        pystray.MenuItem("Exit", quit_app),
    )


def create_tray_icon(toaster: ToastNotifier) -> pystray.Icon:
    """Create the tray icon instance."""
    title = f"{APP_NAME} ({platform.system()})"
    return pystray.Icon(APP_NAME, load_icon(), title, build_menu(toaster))


def main() -> int:
    """Run the tray monitor app."""
    configure_logging()
    logger.info("Starting %s on %s", APP_NAME, platform.platform())

    try:
        toaster = ToastNotifier()
        tray_icon = create_tray_icon(toaster)
        tray_icon.run()
        return 0
    except Exception:
        logger.exception("Fatal error while running tray application")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
