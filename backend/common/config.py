from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "MyAPI"
    database_url: str = "sqlite:///./test.db"
    debug: bool = False

    class Config:
        env_file = ".env"   # 自动读取 .env 文件

settings = Settings()