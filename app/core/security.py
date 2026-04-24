from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
import jwt
from app.config import settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str) -> str:
    """хеширование пароля"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """проверка пароля"""
    return pwd_context.verify(plain_password, hashed_password)

# выдача токена
def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """создание JWT токена"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

def decode_token(token: str) -> dict:
    """декодирование токена с помощью PyJWT"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        # токен просрочен
        return None
    except jwt.InvalidTokenError:
        # токен невалидный
        return None