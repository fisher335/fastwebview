from fastapi import APIRouter, HTTPException
from typing import List
from models.wifi import WiFiNetwork
from services import wifi_scanner, wifi_jammer

router = APIRouter()

@router.get("/scan", response_model=List[WiFiNetwork])
def scan_networks(interface: str = "wlan0"):
    """
    Scan for available WiFi networks.
    """
    networks = wifi_scanner.scan_wifi(interface)
    return networks

@router.post("/jam")
def jam_network(bssid: str, interface: str = "wlan0", count: int = 10):
    """
    Send deauthentication packets to a WiFi network.
    """
    result = wifi_jammer.jam_wifi(bssid, interface, count)
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result)
    return result