from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.adapters.database.models.clients import ClientType


class Credentials(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    phoneNumber: str = Field(pattern=r"^7\d{10}$")
    password: str


class AuthenticationInput(Credentials): ...


class RegistrationInput(Credentials):
    clientType: ClientType


class RefreshTokensInput(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    refreshToken: UUID


class AuthenticationOutput(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    accessToken: str
    accessTokenExpirationTime: datetime
    refreshToken: UUID
    clientName: Optional[str]
    clientType: ClientType


class VerificationInput(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    verification_code: int = Field(alias="verificationCode")


class CodeServiceData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    balance: str
    call_id: int
    created: str
    phone: str
    pincode: str


class CodeServiceOutput(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: str
    data: CodeServiceData


class RecoveryCodeRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    phone_number: str = Field(alias="phoneNumber", pattern=r"^7\d{10}$")


class RecoveryCodeToken(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    recovery_token: str = Field(alias="recoveryToken")


class RecoveryData(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    recovery_token: str = Field(alias="recoveryToken")
    new_password: str = Field(alias="newPassword")
