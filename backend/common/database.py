from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ---------- 数据库配置 ----------
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"  # 使用文件数据库
# SQLite 默认不支持多线程并发写，添加 check_same_thread=False 允许在不同线程中使用
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # 仅 SQLite 需要
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ---------- 依赖项：获取数据库会话 ----------
def get_db():
    """依赖函数，每个请求独立获取一个数据库会话，请求结束后自动关闭"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()