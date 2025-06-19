from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Header, status

from src.adapters.jwt_token import JwtToken
from src.schemas.api.authentication import (
    AuthenticationInput,
    AuthenticationOutput,
    RecoveryCodeRequest,
    RecoveryData,
    RefreshTokensInput,
    RegistrationInput,
    VerificationInput,
)
from src.service.authentication import AuthenticationService
from src.unit_of_work import UnitOfWork
from src.utils.dependencies import provide_jwt_token

authentication_router = APIRouter()


@authentication_router.post("/refresh-token", response_model=AuthenticationOutput)
async def refresh_tokens(
    uow: Annotated[UnitOfWork, Depends(UnitOfWork)],
    background_tasks: BackgroundTasks,
    input: RefreshTokensInput,
    user_agent: Annotated[str, Header()],
    fingerprint: Annotated[str, Header()],
):
    async with uow:
        return await AuthenticationService(uow, background_tasks).refresh_tokens(
            input.refreshToken, user_agent, fingerprint
        )


@authentication_router.post("/authentication", response_model=AuthenticationOutput)
async def authenticate(
    uow: Annotated[UnitOfWork, Depends(UnitOfWork)],
    background_tasks: BackgroundTasks,
    credentials: AuthenticationInput,
    user_agent: Annotated[str, Header()],
    fingerprint: Annotated[str, Header()],
):
    async with uow:
        return await AuthenticationService(uow, background_tasks).login(
            credentials, user_agent, fingerprint
        )


@authentication_router.post("/registration", status_code=status.HTTP_201_CREATED)
async def register(
    uow: Annotated[UnitOfWork, Depends(UnitOfWork)],
    background_tasks: BackgroundTasks,
    credentials: RegistrationInput,
    fingerprint: Annotated[str, Header()],
):
    async with uow:
        await AuthenticationService(uow, background_tasks).register(
            credentials, fingerprint
        )

    return dict()


@authentication_router.post(
    "/check-verification-reg", status_code=status.HTTP_201_CREATED
)
async def registration_verification(
    uow: Annotated[UnitOfWork, Depends(UnitOfWork)],
    background_tasks: BackgroundTasks,
    credentials: VerificationInput,
    fingerprint: Annotated[str, Header()],
):
    async with uow:
        await AuthenticationService(uow, background_tasks).verificate_registration(
            credentials.verification_code, fingerprint
        )

    return dict()


@authentication_router.post("/send-recovery-code", status_code=status.HTTP_201_CREATED)
async def recovery_request(
    uow: Annotated[UnitOfWork, Depends(UnitOfWork)],
    background_tasks: BackgroundTasks,
    credentials: RecoveryCodeRequest,
    fingerprint: Annotated[str, Header()],
    user_agent: Annotated[str, Header()],
):
    async with uow:
        await AuthenticationService(uow, background_tasks).request_recovery(
            credentials, fingerprint
        )
    return dict()


@authentication_router.post(
    "/check-verification-rec", status_code=status.HTTP_201_CREATED
)
async def recovery_verification(
    uow: Annotated[UnitOfWork, Depends(UnitOfWork)],
    background_tasks: BackgroundTasks,
    credentials: VerificationInput,
    fingerprint: Annotated[str, Header()],
):
    async with uow:
        return await AuthenticationService(
            uow, background_tasks
        ).verificate_recovery_code(credentials.verification_code, fingerprint)


@authentication_router.post("/recovery", status_code=status.HTTP_201_CREATED)
async def recovery_password(
    uow: Annotated[UnitOfWork, Depends(UnitOfWork)],
    background_tasks: BackgroundTasks,
    recovery_data: RecoveryData,
):
    async with uow:
        await AuthenticationService(uow, background_tasks).recovery(recovery_data)
    return dict()


@authentication_router.post(
    "/logout", response_model={}, status_code=status.HTTP_200_OK
)
async def logout(
    uow: Annotated[UnitOfWork, Depends(UnitOfWork)],
    background_tasks: BackgroundTasks,
    jwt_token: Annotated[JwtToken, Depends(provide_jwt_token)],
):
    async with uow:
        await AuthenticationService(uow, background_tasks).logout(jwt_token.client_id)
    return dict()
