import subprocess
import re
from typing import List
from models.wifi import WiFiNetwork, EncryptionType
import platform

def scan_wifi(interface: str = "wlan0") -> List[WiFiNetwork]:
    """
    Scan for WiFi networks using aircrack-ng's airodump-ng.
    Requires aircrack-ng installed and running with appropriate permissions.
    """
    # For demonstration, return mock data on Windows or if aircrack-ng not available
    if platform.system() != "Linux":
        return get_mock_networks()
    
    try:
        # Start airodump-ng for a short period
        cmd = ["sudo", "airodump-ng", interface, "--output-format", "csv", "-w", "/tmp/scan", "--write-interval", "1"]
        # Run for 5 seconds
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        proc.wait(timeout=5)
        # Kill the process
        proc.terminate()
        # Read the CSV file
        csv_file = "/tmp/scan-01.csv"
        networks = parse_airodump_csv(csv_file)
        return networks
    except (subprocess.TimeoutExpired, FileNotFoundError, PermissionError):
        # Fallback to mock data
        return get_mock_networks()

def parse_airodump_csv(csv_path: str) -> List[WiFiNetwork]:
    networks = []
    try:
        with open(csv_path, 'r') as f:
            lines = f.readlines()
        # Skip lines until we find the network section
        # Simple parsing for demonstration
        for line in lines:
            if re.match(r'^[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}', line):
                parts = line.split(',')
                if len(parts) >= 14:
                    bssid = parts[0].strip()
                    first_seen = parts[1].strip()
                    last_seen = parts[2].strip()
                    channel = int(parts[3].strip()) if parts[3].strip().isdigit() else 1
                    speed = parts[4].strip()
                    privacy = parts[5].strip()
                    cipher = parts[6].strip()
                    authentication = parts[7].strip()
                    power = int(parts[8].strip()) if parts[8].strip().lstrip('-').isdigit() else -70
                    beacons = parts[9].strip()
                    iv = parts[10].strip()
                    lan_ip = parts[11].strip()
                    id_len = parts[12].strip()
                    ssid = parts[13].strip()
                    # Determine encryption
                    encryption = EncryptionType.WPA2 if "WPA2" in privacy else EncryptionType.WPA if "WPA" in privacy else EncryptionType.WEP if "WEP" in privacy else EncryptionType.OPEN
                    networks.append(WiFiNetwork(
                        ssid=ssid,
                        bssid=bssid,
                        channel=channel,
                        signal_strength=power,
                        encryption=encryption,
                        clients=0
                    ))
    except Exception:
        pass
    return networks

def get_mock_networks() -> List[WiFiNetwork]:
    """Return mock WiFi networks for demonstration."""
    return [
        WiFiNetwork(
            ssid="HomeWiFi",
            bssid="AA:BB:CC:DD:EE:FF",
            channel=6,
            signal_strength=-45,
            encryption=EncryptionType.WPA2,
            clients=3
        ),
        WiFiNetwork(
            ssid="GuestNetwork",
            bssid="11:22:33:44:55:66",
            channel=11,
            signal_strength=-60,
            encryption=EncryptionType.OPEN,
            clients=0
        ),
        WiFiNetwork(
            ssid="Office",
            bssid="FF:EE:DD:CC:BB:AA",
            channel=1,
            signal_strength=-70,
            encryption=EncryptionType.WPA,
            clients=5
        ),
        WiFiNetwork(
            ssid="CafeFreeWiFi",
            bssid="33:44:55:66:77:88",
            channel=3,
            signal_strength=-80,
            encryption=EncryptionType.OPEN,
            clients=8
        ),
    ]