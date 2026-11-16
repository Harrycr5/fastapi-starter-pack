from typing import Literal

from pydantic import BaseModel

from ..users.schemas import UserSessionRead


class TokenRead(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    user: UserSessionRead

