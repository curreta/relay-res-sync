import subprocess
import logging
from typing import Optional


def run_adb(command: str, device_id: Optional[str] = None) -> str:
    """Execute an ADB command and return the output."""
    device_arg = ["-s", device_id] if device_id else []
    full_command = ["adb", *device_arg, *command.split()]
    try:
        result = subprocess.run(
            full_command, check=True, capture_output=True, text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logging.error(f"ADB command failed: {e.stderr}")
        raise


def get_device_id(device_id: Optional[str] = None) -> str:
    """Return the specified device_id or get first connected device."""
    if device_id:
        return device_id
    output = run_adb("devices")
    devices = [
        line.split()[0]
        for line in output.splitlines()
        if line and "device" in line and not line.startswith("List")
    ]
    if not devices:
        raise RuntimeError("No Android devices found")
    return devices[0]
