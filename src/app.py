from fastapi import APIRouter, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from src.api import (
    authentication_router,
)

from src.utils.exceptions import (
    AccessDenied,
    AuthorizationException,
    PlaceOrderForeignKeyError,
    ResultNotFound,
    UserAlreadyExist,
    UserNotRegistered,
    VerificationException,
    WrongCredentials,
)

app = FastAPI(
    title="udom backend",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

main_app_router = APIRouter(prefix="/api")

main_app_router.include_router(authentication_router, tags=["Authentication"])

app.include_router(main_app_router)


@app.exception_handler(ResultNotFound)
async def not_found_exception_handler(request: Request, exc: ResultNotFound):
    return JSONResponse(
        status_code=404,
        content={"detail": "Result not found"},
    )


@app.exception_handler(AuthorizationException)
async def authorization_exception_handler(
    request: Request, exc: AuthorizationException
):
    return JSONResponse(
        status_code=401,
        content={"detail": "Provided token mailformed"},
    )


@app.exception_handler(WrongCredentials)
async def login_exception_handler(request: Request, exc: WrongCredentials):
    return JSONResponse(
        status_code=401,
        content={"detail": "Wrong credentials provided"},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.errors(), "body": exc.body},
    )


@app.exception_handler(VerificationException)
async def verification_exception_handler(request: Request, exc: VerificationException):
    return JSONResponse(
        status_code=401,
        content={"detail": "Verification code is incorrect"},
    )


@app.exception_handler(UserNotRegistered)
async def user_not_registered(request: Request, exc: UserNotRegistered):
    return JSONResponse(
        status_code=403, content={"detail": "No authorization tokens provided"}
    )


@app.exception_handler(PlaceOrderForeignKeyError)
async def place_orders_foreign_key_error(
    request: Request, exc: PlaceOrderForeignKeyError
):
    return JSONResponse(status_code=400, content={"detail": "Place order FK error"})


@app.exception_handler(AccessDenied)
async def access_denied(request: Request, exc: AccessDenied):
    return JSONResponse(
        status_code=403, content={"detail": "You have no right to access this resource"}
    )


@app.exception_handler(UserAlreadyExist)
async def user_already_exist(request: Request, exc: AccessDenied):
    return JSONResponse(
        status_code=409, content={"detail": "User with this credential already exist"}
    )
