from typing import Any

from src.adapters.database.models import Client, Token
from src.adapters.jwt_token import JwtToken
from src.schemas.api.authentication import AuthenticationOutput, RegistrationInput


def to_authentication_output(
    client_record: Client, access_token: JwtToken, refresh_token: Token
) -> AuthenticationOutput:
    return AuthenticationOutput(
        accessToken=access_token.encode(),
        refreshToken=refresh_token.refresh_token,
        accessTokenExpirationTime=access_token.exp,
        clientName=client_record.first_name,
        clientType=client_record.client_type,
    )


def to_registration_database_fields(
    client_info: RegistrationInput,
) -> dict[str, Any]:
    return {
        "phone": client_info.phoneNumber,
        "password": client_info.password,
        "client_type": client_info.clientType,
    }
