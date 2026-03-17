from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from typing import List
import json
import asyncio
from models.wifi import WiFiNetwork
from services import wifi_scanner, wifi_jammer

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message: dict, websocket: WebSocket):
        await websocket.send_text(json.dumps(message))

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_text(json.dumps(message))

manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        await websocket.send_text(json.dumps({
            "type": "connected",
            "message": "WebSocket连接已建立"
        }))

        
        while True:
            data = await websocket.receive_text()
            try:
                request = json.loads(data)
                action = request.get("action")
                params = request.get("params", {})
                
                if action == "scan":
                    interface = params.get("interface", "wlan0")
                    networks = wifi_scanner.scan_wifi(interface)
                    await manager.send_message({
                        "type": "scan_result",
                        "data": [n.model_dump() for n in networks]
                    }, websocket)
                    
                elif action == "jam":
                    bssid = params.get("bssid")
                    interface = params.get("interface", "wlan0")
                    count = params.get("count", 10)
                    
                    if not bssid:
                        await manager.send_message({
                            "type": "error",
                            "message": "缺少bssid参数"
                        }, websocket)
                        continue
                    
                    result = wifi_jammer.jam_wifi(bssid, interface, count)
                    await manager.send_message({
                        "type": "jam_result",
                        "data": result
                    }, websocket)
                    
                else:
                    await manager.send_message({
                        "type": "error",
                        "message": f"未知的操作: {action}"
                    }, websocket)
                    
            except json.JSONDecodeError:
                await manager.send_message({
                    "type": "error",
                    "message": "无效的JSON格式"
                }, websocket)
            except Exception as e:
                await manager.send_message({
                    "type": "error",
                    "message": str(e)
                }, websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast({
            "type": "disconnected",
            "message": "客户端已断开连接"
        })

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