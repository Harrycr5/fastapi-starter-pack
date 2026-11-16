from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, SecretStr

from ..users.schemas import UserSessionRead


class TokenRead(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: Literal["bearer"] = "bearer"
    user: UserSessionRead


class RefreshRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    refresh_token: SecretStr = Field(min_length=1, max_length=512)
