from typing import Tuple

import jwt
from fastapi import Query, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from starlette import status


# 方式一：直接返回元组（简单场景）
def pagination(
        page: int = Query(1, ge=1, description="页码，从1开始"),
        size: int = Query(20, ge=1, le=100, description="每页条数，最大100"),
) -> Tuple[int, int]:
    """依赖项：返回 (skip, limit) 方便用于数据库查询"""
    skip = (page - 1) * size
    return skip, size


# 模拟用户模型
class User(BaseModel):
    id: int
    username: str
    role: str


# JWT 配置（实际应从环境变量读取）
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

# 使用 HTTPBearer 安全方案，自动提取 Bearer token
security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """依赖项：从请求头解析 JWT 并返回当前用户"""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        username: str = payload.get("username")
        role: str = payload.get("role")
        if user_id is None or username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的令牌内容",
            )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效或过期的令牌",
        )
    return User(id=user_id, username=username, role=role)


# 可选：更细粒度的权限依赖
def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """依赖项：要求当前用户是管理员"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限",
        )
    return current_user
