import os
import threading
import webview
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from routers import wifi

app = FastAPI(title="WiFi Scan & Jammer API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(wifi.router, prefix="/api/wifi", tags=["wifi"])


static_dir = os.path.join(os.path.dirname(__file__), "dist")
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

@app.get("/")
def root():
    return {"message": "WiFi Scan & Jammer API"}


def start_server():
    """在新线程中启动FastAPI服务器"""
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")


if __name__ == '__main__':
    # 在新线程中启动FastAPI服务器
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    # 创建PyWebView窗口，加载Vue页面
    # 开发环境：http://localhost:5173 (Vue dev server)
    # 生产环境：http://localhost:8000 (FastAPI挂载的静态文件)
    window = webview.create_window(
        title="我的Vue+FastAPI应用",
        url="http://localhost:8000",  # FastAPI服务的地址
        width=1200,
        height=800,
        resizable=True,
        text_select=True,  # 允许选择文本
    )

    # 启动PyWebView
    webview.start()