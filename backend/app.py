import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles

from common import config
from common.database import get_db
from routers import wifi


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- 启动逻辑 (yield 之前) ---
    print("应用程序启动：正在创建数据库连接池...")
    print(f"数据库地址: {config.settings.database_url}")
    # 初始化数据库连接池，并存储在 app.state 中
    # app.state.db_pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=10)
    print("数据库连接池创建成功")

    # yield 关键字是分隔点，此时应用已准备好接收请求
    yield

    # --- 关闭逻辑 (yield 之后) ---
    print("应用程序关闭：正在关闭数据库连接池...")
    # 关闭数据库连接池，释放资源
    # await app.state.db_pool.close()
    print("数据库连接池已关闭")

app = FastAPI(title="WiFi Scan & Jammer API", version="1.0.0",lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(wifi.router, prefix="/api/wifi", tags=["wifi"])
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "type": "custom"}
    )


static_dir = os.path.join(os.path.dirname(__file__), "dist")
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

@app.get("/")
def root(db=Depends(get_db)):
    return {"message": "WiFi Scan & Jammer API"}
