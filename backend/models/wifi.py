from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class EncryptionType(str, Enum):
    WPA2 = "WPA2"
    WPA = "WPA"
    WEP = "WEP"
    OPEN = "OPEN"

class STA(BaseModel):
    mac: str
    bssid: str  # 连接的AP的BSSID
    signal_strength: int  # dBm
    packets: int = 0

class WiFiNetwork(BaseModel):
    ssid: str
    bssid: str
    channel: int
    signal_strength: int  # dBm
    encryption: EncryptionType
    clients: Optional[List[STA]] = None