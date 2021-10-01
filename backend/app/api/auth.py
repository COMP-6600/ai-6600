# Routing and Database
from fastapi import APIRouter, HTTPException, Depends, status, Header
from sqlalchemy.orm import Session

# Model and Schema
# import app.db.schemas as schema
# import app.db.models as model
import app.db.structures as structure

# CRUD
from app.db.crud import db_authentication

# Dependencies
from pydantic import BaseModel, validator,  root_validator
from uuid import uuid4
from app.core import security
from app.core.config import settings
from app.utils.dependencies import get_db, validate_api_key


# -------------------
#  ROUTER DEFINITION
# -------------------
router = APIRouter(
    prefix="/api/auth",
    tags=["auth"],
    responses={404: {"status": "undocumented endpoint", "detail": "route was not found"}},
)


# -------------------
#   INITIALIZATION
# -------------------
@router.post('/instance', response_model=structure.Token)
def get_instance(x_api_key: str = Header(None), db: Session = Depends(get_db)) -> dict[str, str]:
    """ Returns an access token if the correct API Key is provided. Returns a JWT to maintain session.

    **x_api_key** Corresponds to the api key passed as a header
    """
    # Verify key
    if not validate_api_key(x_api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Timestamp this instance request and set instance token
    session = db_authentication.create_session(db, token=uuid4().hex)

    # Generate instance but don't actually instantiate it until we make any requests that require it
    return {
        "access_token": security.generate_token(
            payload={
                "instance": session.instance
            },
            subject='client',
            expires_delta=settings.ACCESS_TOKEN_EXPIRATION
        ),
        "token_type": "bearer"
    }
