from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    exp: Optional[int] = None


class TokenData(BaseModel):
    user_id: Optional[int] = None
    username: Optional[str] = None
    roles: Optional[list] = None
    permissions: Optional[list] = None 