from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    """ Maintains the structure of the payload of a JWT """
    sub: str
