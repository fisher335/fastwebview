import random
import subprocess
import re
from typing import List, Dict
from models.wifi import WiFiNetwork, STA, EncryptionType
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
        proc.wait(timeout=20)
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
    clients: Dict[str, List[STA]] = {}
    try:
        with open(csv_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        # Find the separator between APs and clients
        ap_section = True
        for line in lines:
            line = line.strip()
            # Skip header lines
            if line.startswith("BSSID") or line.startswith("Station MAC"):
                if "Station MAC" in line:
                    ap_section = False
                continue
            if not line:
                continue

            # Parse MAC address
            mac_match = re.match(
                r'^([0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2})', line)
            if not mac_match:
                continue

            mac = mac_match.group(1).upper()
            parts = [p.strip() for p in line.split(',')]

            if ap_section:
                # Parse AP
                if len(parts) >= 14:
                    bssid = mac
                    channel_str = parts[3].strip() if len(parts) > 3 else "1"
                    channel = int(channel_str) if channel_str.isdigit() else 1

                    power_str = parts[8].strip() if len(parts) > 8 else "-70"
                    try:
                        power = int(power_str)
                    except ValueError:
                        power = -70

                    privacy = parts[5].strip() if len(parts) > 5 else ""
                    encryption = EncryptionType.WPA2 if "WPA2" in privacy else EncryptionType.WPA if "WPA" in privacy else EncryptionType.WEP if "WEP" in privacy else EncryptionType.OPEN

                    ssid = parts[13].strip() if len(parts) > 13 else ""

                    networks.append(WiFiNetwork(
                        ssid=ssid,
                        bssid=bssid,
                        channel=channel,
                        signal_strength=power,
                        encryption=encryption,
                        clients=[]
                    ))
            else:
                # Parse client (STA)
                if len(parts) >= 6:
                    # Client's connected AP BSSID is in the second column
                    connected_bssid = parts[1].strip().upper() if len(parts) > 1 else ""

                    power_str = parts[3].strip() if len(parts) > 3 else "-70"
                    try:
                        power = int(power_str)
                    except ValueError:
                        power = -70

                    packets_str = parts[4].strip() if len(parts) > 4 else "0"
                    try:
                        packets = int(packets_str)
                    except ValueError:
                        packets = 0

                    if connected_bssid and connected_bssid != "(not associated)":
                        sta = STA(
                            mac=mac,
                            bssid=connected_bssid,
                            signal_strength=power,
                            packets=packets
                        )
                        if connected_bssid not in clients:
                            clients[connected_bssid] = []
                        clients[connected_bssid].append(sta)

        # Associate clients with their APs
        for network in networks:
            if network.bssid in clients:
                network.clients = clients[network.bssid]
            else:
                network.clients = []

    except Exception as e:
        print(f"Error parsing CSV: {e}")

    return networks


def get_mock_networks() -> List[WiFiNetwork]:
    """Return mock WiFi networks for demonstration."""
    aa = [
        WiFiNetwork(
            ssid="HomeWiFi",
            bssid="AA:BB:CC:DD:EE:FF",
            channel=6,
            signal_strength=-45,
            encryption=EncryptionType.WPA2,
            clients=[
                STA(mac="11:22:33:44:55:77", bssid="AA:BB:CC:DD:EE:FF", signal_strength=-50, packets=1250),
                STA(mac="11:22:33:44:55:88", bssid="AA:BB:CC:DD:EE:FF", signal_strength=-55, packets=890),
                STA(mac="11:22:33:44:55:99", bssid="AA:BB:CC:DD:EE:FF", signal_strength=-60, packets=456),
            ]
        ),
        WiFiNetwork(
            ssid="GuestNetwork",
            bssid="11:22:33:44:55:66",
            channel=11,
            signal_strength=-60,
            encryption=EncryptionType.OPEN,
            clients=[]
        ),
        WiFiNetwork(
            ssid="Office",
            bssid="FF:EE:DD:CC:BB:AA",
            channel=1,
            signal_strength=-70,
            encryption=EncryptionType.WPA,
            clients=[
                STA(mac="AA:BB:CC:DD:EE:01", bssid="FF:EE:DD:CC:BB:AA", signal_strength=-65, packets=2340),
                STA(mac="AA:BB:CC:DD:EE:02", bssid="FF:EE:DD:CC:BB:AA", signal_strength=-72, packets=1567),
                STA(mac="AA:BB:CC:DD:EE:03", bssid="FF:EE:DD:CC:BB:AA", signal_strength=-75, packets=890),
                STA(mac="AA:BB:CC:DD:EE:04", bssid="FF:EE:DD:CC:BB:AA", signal_strength=-78, packets=432),
                STA(mac="AA:BB:CC:DD:EE:05", bssid="FF:EE:DD:CC:BB:AA", signal_strength=-80, packets=210),
            ]
        ),
        WiFiNetwork(
            ssid="CafeFreeWiFi",
            bssid="33:44:55:66:77:88",
            channel=3,
            signal_strength=-80,
            encryption=EncryptionType.OPEN,
            clients=[
                STA(mac="BB:CC:DD:EE:FF:01", bssid="33:44:55:66:77:88", signal_strength=-70, packets=5678),
                STA(mac="BB:CC:DD:EE:FF:02", bssid="33:44:55:66:77:88", signal_strength=-75, packets=3456),
            ]
        ),
        WiFiNetwork(
            ssid="CafeFreeWiFi",
            bssid="33:44:55:66:77:88",
            channel=3,
            signal_strength=-80,
            encryption=EncryptionType.OPEN,
            clients=[
                STA(mac="BB:CC:DD:EE:FF:01", bssid="33:44:55:66:77:88", signal_strength=-70, packets=5678),
                STA(mac="BB:CC:DD:EE:FF:02", bssid="33:44:55:66:77:88", signal_strength=-75, packets=3456),
            ]
        ),
        WiFiNetwork(
            ssid="CafeFreeWiFi",
            bssid="33:44:55:66:77:88",
            channel=3,
            signal_strength=-80,
            encryption=EncryptionType.OPEN,
            clients=[
                STA(mac="BB:CC:DD:EE:FF:01", bssid="33:44:55:66:77:88", signal_strength=-70, packets=5678),
                STA(mac="BB:CC:DD:EE:FF:02", bssid="33:44:55:66:77:88", signal_strength=-75, packets=3456),
            ]
        ),
        WiFiNetwork(
            ssid="CafeFreeWiFi",
            bssid="33:44:55:66:77:88",
            channel=3,
            signal_strength=-80,
            encryption=EncryptionType.OPEN,
            clients=[
                STA(mac="BB:CC:DD:EE:FF:01", bssid="33:44:55:66:77:88", signal_strength=-70, packets=5678),
                STA(mac="BB:CC:DD:EE:FF:02", bssid="33:44:55:66:77:88", signal_strength=-75, packets=3456),
            ]
        ),        WiFiNetwork(
            ssid="CafeFreeWiFi",
            bssid="33:44:55:66:77:88",
            channel=3,
            signal_strength=-80,
            encryption=EncryptionType.OPEN,
            clients=[
                STA(mac="BB:CC:DD:EE:FF:01", bssid="33:44:55:66:77:88", signal_strength=-70, packets=5678),
                STA(mac="BB:CC:DD:EE:FF:02", bssid="33:44:55:66:77:88", signal_strength=-75, packets=3456),
            ]
        ),
        WiFiNetwork(
            ssid="CafeFreeWiFi",
            bssid="33:44:55:66:77:88",
            channel=3,
            signal_strength=-80,
            encryption=EncryptionType.OPEN,
            clients=[
                STA(mac="BB:CC:DD:EE:FF:01", bssid="33:44:55:66:77:88", signal_strength=-70, packets=5678),
                STA(mac="BB:CC:DD:EE:FF:02", bssid="33:44:55:66:77:88", signal_strength=-75, packets=3456),
            ]
        ),
        WiFiNetwork(
            ssid="CafeFreeWiFi",
            bssid="33:44:55:66:77:88",
            channel=3,
            signal_strength=-80,
            encryption=EncryptionType.OPEN,
            clients=[
                STA(mac="BB:CC:DD:EE:FF:01", bssid="33:44:55:66:77:88", signal_strength=-70, packets=5678),
                STA(mac="BB:CC:DD:EE:FF:02", bssid="33:44:55:66:77:88", signal_strength=-75, packets=3456),
            ]
        ),
        WiFiNetwork(
            ssid="CafeFreeWiFi",
            bssid="33:44:55:66:77:88",
            channel=3,
            signal_strength=-80,
            encryption=EncryptionType.OPEN,
            clients=[
                STA(mac="BB:CC:DD:EE:FF:01", bssid="33:44:55:66:77:88", signal_strength=-70, packets=5678),
                STA(mac="BB:CC:DD:EE:FF:02", bssid="33:44:55:66:77:88", signal_strength=-75, packets=3456),
            ]
        ),

    ]
    if random.randint(1, 10) > 5:
        aa.append(WiFiNetwork(
            ssid="补充内容",
            bssid="33:44:52:66:77:88",
            channel=3,
            signal_strength=-80,
            encryption=EncryptionType.OPEN,
            clients=[
                STA(mac="BB:CC:DD:EE:FF:01", bssid="33:44:55:66:77:88", signal_strength=-70, packets=5678),
                STA(mac="BB:CC:DD:EE:FF:02", bssid="33:44:55:66:77:88", signal_strength=-75, packets=3456),
            ]
        ))
    return aa
