"""
安全和认证相关功能
包括密码哈希、JWT Token生成/验证、数据加密等
"""

from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet
import secrets

from app.core.config import settings

# ============ 密码哈希 ============
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码

    Args:
        plain_password: 明文密码
        hashed_password: 哈希后的密码

    Returns:
        bool: 密码是否匹配
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    密码哈希

    Args:
        password: 明文密码

    Returns:
        str: 哈希后的密码
    """
    return pwd_context.hash(password)


# ============ JWT Token ============
def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    创建JWT访问令牌

    Args:
        data: 要编码的数据(通常包含用户ID)
        expires_delta: 过期时间增量

    Returns:
        str: JWT token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    创建JWT刷新令牌

    Args:
        data: 要编码的数据

    Returns:
        str: JWT refresh token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """
    解码JWT token

    Args:
        token: JWT token字符串

    Returns:
        Optional[dict]: 解码后的数据,解码失败返回None
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def verify_token(token: str, token_type: str = "access") -> Optional[dict]:
    """
    验证JWT token

    Args:
        token: JWT token
        token_type: token类型 ("access" 或 "refresh")

    Returns:
        Optional[dict]: token有效返回payload,无效返回None
    """
    payload = decode_token(token)

    if not payload:
        return None

    # 验证token类型
    if payload.get("type") != token_type:
        return None

    # 验证是否过期(decode_token已经检查,这里是double check)
    exp = payload.get("exp")
    if not exp or datetime.fromtimestamp(exp) < datetime.utcnow():
        return None

    return payload


def verify_access_token(token: str) -> str:
    """
    验证access token并返回用户ID

    Args:
        token: JWT access token

    Returns:
        str: 用户ID

    Raises:
        ValueError: token无效时抛出异常
    """
    payload = verify_token(token, token_type="access")

    if not payload:
        raise ValueError("Invalid or expired access token")

    user_id = payload.get("sub")
    if not user_id:
        raise ValueError("Token missing user ID")

    return user_id


def verify_refresh_token(token: str) -> str:
    """
    验证refresh token并返回用户ID

    Args:
        token: JWT refresh token

    Returns:
        str: 用户ID

    Raises:
        ValueError: token无效时抛出异常
    """
    payload = verify_token(token, token_type="refresh")

    if not payload:
        raise ValueError("Invalid or expired refresh token")

    user_id = payload.get("sub")
    if not user_id:
        raise ValueError("Token missing user ID")

    return user_id


# ============ 数据加密 ============
class DataEncryption:
    """
    数据加密/解密工具类
    用于健康数据等敏感信息的端到端加密
    """

    def __init__(self, key: Optional[str] = None):
        """
        初始化加密器

        Args:
            key: 加密密钥(base64编码),不提供则使用配置中的密钥
        """
        encryption_key = key or settings.ENCRYPTION_KEY

        # 确保密钥格式正确
        if not encryption_key:
            # 生成随机密钥(仅用于开发环境)
            encryption_key = Fernet.generate_key().decode()
            print(f"⚠️  Warning: Using random encryption key (dev only): {encryption_key}")

        self.cipher = Fernet(encryption_key.encode() if isinstance(encryption_key, str) else encryption_key)

    def encrypt(self, data: Union[str, bytes]) -> str:
        """
        加密数据

        Args:
            data: 要加密的数据

        Returns:
            str: 加密后的数据(base64编码)
        """
        if isinstance(data, str):
            data = data.encode()

        encrypted = self.cipher.encrypt(data)
        return encrypted.decode()

    def decrypt(self, encrypted_data: Union[str, bytes]) -> str:
        """
        解密数据

        Args:
            encrypted_data: 加密的数据

        Returns:
            str: 解密后的数据
        """
        if isinstance(encrypted_data, str):
            encrypted_data = encrypted_data.encode()

        decrypted = self.cipher.decrypt(encrypted_data)
        return decrypted.decode()


# ============ 其他安全工具 ============
def generate_random_token(length: int = 32) -> str:
    """
    生成随机令牌
    用于API密钥、重置密码令牌等

    Args:
        length: 令牌长度

    Returns:
        str: 随机令牌
    """
    return secrets.token_urlsafe(length)


def generate_verification_code(length: int = 6) -> str:
    """
    生成数字验证码
    用于短信验证等

    Args:
        length: 验证码长度

    Returns:
        str: 数字验证码
    """
    return ''.join([str(secrets.randbelow(10)) for _ in range(length)])


# 全局加密器实例
encryptor = DataEncryption()
