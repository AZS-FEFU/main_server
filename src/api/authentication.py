from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Header, status

from src.adapters.jwt_token import JwtToken
from src.schemas.api.authentication import (
    AuthenticationInput,
    AuthenticationOutput,
)
from src.unit_of_work import UnitOfWork
from src.utils.dependencies import provide_jwt_token

authentication_router = APIRouter()


@authentication_router.post("/authentication", response_model=AuthenticationOutput)
async def authenticate(
    uow: Annotated[UnitOfWork, Depends(UnitOfWork)],
    background_tasks: BackgroundTasks,
    credentials: AuthenticationInput,
    user_agent: Annotated[str, Header()],
    fingerprint: Annotated[str, Header()],
):
    pass
    # async with uow:
    #     return await AuthenticationService(uow, background_tasks).login(
    #         credentials, user_agent, fingerprint
    #     )


@authentication_router.post("/registration", status_code=status.HTTP_201_CREATED)
async def register(
    uow: Annotated[UnitOfWork, Depends(UnitOfWork)],
    background_tasks: BackgroundTasks,
    credentials: dict,
    fingerprint: Annotated[str, Header()],
):
    # async with uow:
    #     await AuthenticationService(uow, background_tasks).register(
    #         credentials, fingerprint
    #     )

    return dict()
