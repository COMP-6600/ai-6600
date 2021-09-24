from pydantic import BaseModel


class AuthenticationBase(BaseModel):
    pass


class AuthenticationCreate(AuthenticationBase):
    pass


class AuthenticationUpdate(AuthenticationBase):
    pass
