# Time management
import arrow

# Typing and Validation
from typing import Any, Union

# JWT and cryptography
from jose import jwt  # noqa
from passlib.context import CryptContext

# Import local settings
from app.core.config import settings

# TODO: Not used in this context yet (or ever) as there is no password validation
password_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def generate_token(payload: dict, subject: Union[str, Any], expires_delta: int = None) -> str:
    """ Generates a JWT token to be passed in header requests and provides access for a limited time without re-auth. """
    return jwt.encode(
        claims={
            'iat': arrow.utcnow().datetime,
            'exp': arrow.utcnow().shift(minutes=expires_delta or settings.ACCESS_TOKEN_EXPIRATION).datetime,
            'sub': str(subject),
            **payload
        },
        key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
