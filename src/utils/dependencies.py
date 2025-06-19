from datetime import datetime, timezone
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

# from src.adapters.database.models.clients import ClientType
from src.adapters.jwt_token import JwtToken

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="authenticaition", auto_error=False)


async def provide_jwt_token(
    encoded_token: Annotated[str | None, Depends(oauth2_scheme)] = None,
) -> JwtToken:
    if encoded_token is None:
        return JwtToken(
            exp=datetime.now(timezone.utc), client_id=0
        )
    return JwtToken.decode(encoded_token)
