import threading

import uvicorn
import webview

from app import app

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
        title="WIFI扫描",
        url="http://localhost:8000",  # FastAPI服务的地址
        width=1200,
        height=800,
        resizable=True,
        text_select=True,  # 允许选择文本
    )

    # 启动PyWebView
    webview.start()