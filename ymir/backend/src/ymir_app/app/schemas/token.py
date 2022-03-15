from pydantic import BaseModel

from .common import Common


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenOut(Common):
    access_token: str
    token_type: str
    result: Token


class TokenPayload(BaseModel):
    id: int
    role: str
