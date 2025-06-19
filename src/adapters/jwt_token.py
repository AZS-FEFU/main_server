from dataclasses import asdict, dataclass
from datetime import datetime, timezone

import jwt
from jwt.exceptions import DecodeError, ExpiredSignatureError

# from src.adapters.database.models.clients import ClientType
from src.settings import settings
from src.utils.exceptions import JwtExpired, JwtInvalid


@dataclass
class JwtToken:
    exp: datetime
    client_id: int
    # client_type: ClientType

    @staticmethod
    def _serialize_expiration_date(timestamp):
        expiration_date = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        return expiration_date

    @classmethod
    def decode(cls, encoded_token):
        try:
            payload = jwt.decode(
                jwt=encoded_token,
                key=settings.JWT_SECRET,
                algorithms=["HS256"],
            )
        except DecodeError:
            raise JwtInvalid
        except ExpiredSignatureError:
            raise JwtExpired

        payload["exp"] = cls._serialize_expiration_date(payload["exp"])
        return cls(**payload)

    def encode(self) -> str:
        return jwt.encode(
            payload={k: v for k, v in asdict(self).items() if v is not None},
            key=settings.JWT_SECRET,
            algorithm="HS256",
        )
