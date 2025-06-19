from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field



class Credentials(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    phoneNumber: str = Field(pattern=r"^7\d{10}$")
    password: str


class AuthenticationInput(Credentials): ...


# class RegistrationInput(Credentials):
#     clientType: ClientType


class RefreshTokensInput(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    refreshToken: UUID


class AuthenticationOutput(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    accessToken: str
    accessTokenExpirationTime: datetime
    refreshToken: UUID
    clientName: Optional[str]
    # clientType: ClientType
