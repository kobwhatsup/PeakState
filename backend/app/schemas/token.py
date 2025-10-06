"""
JWT令牌相关模式
"""

from pydantic import BaseModel, Field


class Token(BaseModel):
    """访问令牌响应"""
    access_token: str = Field(..., description="JWT访问令牌")
    refresh_token: str = Field(..., description="JWT刷新令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间(秒)")


class TokenPayload(BaseModel):
    """JWT令牌载荷"""
    sub: str = Field(..., description="用户ID(UUID字符串)")
    exp: int = Field(..., description="过期时间戳")
    iat: int = Field(..., description="签发时间戳")
    type: str = Field(..., description="令牌类型(access/refresh)")


class RefreshTokenRequest(BaseModel):
    """刷新令牌请求"""
    refresh_token: str = Field(..., description="刷新令牌")


class RefreshTokenResponse(BaseModel):
    """刷新令牌响应"""
    access_token: str = Field(..., description="新的访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间(秒)")
