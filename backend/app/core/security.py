from datetime import datetime, timedelta
from typing import Any, Union

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

ALGORITHM = 'HS256'


def generate_token(payload: dict, subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    if not expires_delta:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRATION)
    to_encode = {
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + expires_delta,
        'sub': str(subject),
        **payload
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plaintext_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plaintext_password, hashed_password)


def hash_password(plaintext_password: str) -> str:
    return pwd_context.hash(plaintext_password)
