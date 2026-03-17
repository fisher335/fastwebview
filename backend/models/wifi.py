from pydantic import BaseModel
from typing import Optional
from enum import Enum

class EncryptionType(str, Enum):
    WPA2 = "WPA2"
    WPA = "WPA"
    WEP = "WEP"
    OPEN = "OPEN"

class WiFiNetwork(BaseModel):
    ssid: str
    bssid: str
    channel: int
    signal_strength: int  # dBm
    encryption: EncryptionType
    clients: Optional[int] = 0