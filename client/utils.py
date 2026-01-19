import subprocess
import hashlib
import sys
import os

def get_hwid():
    """
    Generates a unique hardware ID for the machine.
    Combines UUID and Processor ID for stability.
    """
    try:
        # Get machine UUID
        cmd_uuid = "wmic csproduct get uuid"
        uuid_output = subprocess.check_output(cmd_uuid, shell=True).decode().splitlines()
        uuid = next((line.strip() for line in uuid_output if line.strip() and "UUID" not in line), "")
        
        # Get processor ID
        cmd_cpu = "wmic cpu get processorid"
        cpu_output = subprocess.check_output(cmd_cpu, shell=True).decode().splitlines()
        cpu = next((line.strip() for line in cpu_output if line.strip() and "ProcessorId" not in line), "")
        
        if uuid and cpu:
            raw = f"{uuid}-{cpu}"
            return hashlib.sha256(raw.encode()).hexdigest()
        else:
            raise Exception("Incomplete WMIC data")
    except Exception:
        # Fallback using MAC address via uuid module
        try:
            import uuid as _uuid_mod
            mac = _uuid_mod.getnode()
            return hashlib.sha256(str(mac).encode()).hexdigest()
        except Exception:
            return "UNKNOWN_HWID_FALLBACK"

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
