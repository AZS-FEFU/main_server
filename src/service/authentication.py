from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import BackgroundTasks
from pydantic import BaseModel

from src.adapters.jwt_token import JwtToken
from src.schemas.api.authentication import (
    AuthenticationInput,
    AuthenticationOutput,
    RecoveryCodeRequest,
    RecoveryCodeToken,
    RecoveryData,
    RegistrationInput,
)
from src.schemas.mappers import (
    to_authentication_output,
    to_registration_database_fields,
)
from src.settings import settings
from src.unit_of_work import UnitOfWork
from src.utils.exceptions import (
    ResultNotFound,
    UserAlreadyExist,
    VerificationException,
    WrongCredentials,
)


class RegistrationData(BaseModel):
    client_info: RegistrationInput
    timestamp: datetime
    verification_code: int


class RecoveryRequestData(BaseModel):
    client_info: RecoveryCodeRequest
    timestamp: datetime
    verification_code: int


registration_queue: dict[str, RegistrationData] = {}
recovery_queue: dict[str, RecoveryRequestData] = {}


class AuthenticationService:
    def __init__(self, uow: UnitOfWork, background_tasks: BackgroundTasks):
        self.uow = uow
        self.background_tasks = background_tasks

    async def _add_to_registration_queue(
        self, fingerprint: str, client_info: RegistrationInput
    ):
        registration_queue[fingerprint] = RegistrationData(
            client_info=client_info,
            timestamp=datetime.now(timezone.utc),
            verification_code=await self.uow.verifications.send_verification_code(
                client_info.phoneNumber
            ),
        )

    async def _add_to_recovery_queue(
        self, fingerprint: str, client_info: RecoveryCodeRequest
    ):
        recovery_queue[fingerprint] = RecoveryRequestData(
            client_info=client_info,
            timestamp=datetime.now(timezone.utc),
            verification_code=await self.uow.verifications.send_verification_code(
                client_info.phone_number
            ),
        )

    async def login(
        self, credentials: AuthenticationInput, user_agent: str, fingerprint: str
    ) -> AuthenticationOutput:
        client = await self.uow.repositories.client.authenticate(
            phone=credentials.phoneNumber, password=credentials.password
        )

        if client.id == 0:
            raise WrongCredentials

        refresh_token = await self.uow.repositories.refresh_token_repository.generate(
            client_id=client.id,
            user_agent=user_agent,
            fingerprint=fingerprint,
        )

        await self.uow.commit()

        return to_authentication_output(
            client_record=client,
            access_token=JwtToken(
                exp=datetime.now(tz=timezone.utc)
                + timedelta(minutes=settings.JWT_TOKEN_LIFETIME),
                client_id=client.id,
                client_type=client.client_type,
            ),
            refresh_token=refresh_token,
        )

    async def refresh_tokens(
        self, refresh_token: UUID, user_agent: str, fingerprint: str
    ) -> AuthenticationOutput:
        token = await self.uow.repositories.refresh_token_repository.refresh(
            refresh_token, user_agent, fingerprint
        )
        await self.uow.commit()

        return to_authentication_output(
            client_record=token.client,
            access_token=JwtToken(
                exp=datetime.now(tz=timezone.utc)
                + timedelta(minutes=settings.JWT_TOKEN_LIFETIME),
                client_id=token.client.id,
                client_type=token.client.client_type,
            ),
            refresh_token=token,
        )

    async def register(self, credentials: RegistrationInput, fingerprint: str) -> None:
        try:
            await self.uow.repositories.client.find_one(phone=credentials.phoneNumber)
            raise UserAlreadyExist("User with this phone number already exist")
        except ResultNotFound:
            pass

        self.background_tasks.add_task(
            self._add_to_registration_queue,
            fingerprint=fingerprint,
            client_info=credentials,
        )

    async def verificate_registration(
        self, verification_code: int, fingerprint: str
    ) -> None:
        data = registration_queue.get(fingerprint)
        if not data:
            raise VerificationException
        if data.verification_code != verification_code:
            raise WrongCredentials

        del registration_queue[fingerprint]
        await self.uow.repositories.client.register(
            **to_registration_database_fields(data.client_info)
        )
        await self.uow.commit()

    async def logout(self, client_id: int) -> None:
        if client_id == 0:
            raise VerificationException

        try:
            await self.uow.repositories.refresh_token_repository.find_one(
                client_id=client_id
            )
        except ResultNotFound:
            raise WrongCredentials

        await self.uow.repositories.refresh_token_repository.delete_one(id=client_id)
        await self.uow.commit()

    async def request_recovery(
        self, client_info: RecoveryCodeRequest, fingerprint: str
    ) -> None:
        await self.uow.repositories.client.find_one(phone=client_info.phone_number)
        self.background_tasks.add_task(
            self._add_to_recovery_queue,
            fingerprint=fingerprint,
            client_info=client_info,
        )

    async def verificate_recovery_code(
        self, verification_code: int, fingerprint: str
    ) -> RecoveryCodeToken:
        code_data = recovery_queue.get(fingerprint)
        if code_data is None:
            raise VerificationException
        if code_data.verification_code != verification_code:
            raise WrongCredentials
        del recovery_queue[fingerprint]
        client = await self.uow.repositories.client.find_one(
            phone=code_data.client_info.phone_number
        )
        return RecoveryCodeToken(
            recovery_token=JwtToken(
                exp=datetime.now(tz=timezone.utc)
                + timedelta(minutes=settings.JWT_TOKEN_LIFETIME),
                client_id=client.id,
                client_type=client.client_type,
            ).encode()
        )

    async def recovery(self, recovery_data: RecoveryData) -> None:
        token = JwtToken.decode(recovery_data.recovery_token)
        await self.uow.repositories.client.change_password(
            token.client_id, recovery_data.new_password
        )
        await self.uow.commit()
