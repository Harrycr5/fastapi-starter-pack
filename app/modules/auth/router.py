from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies import DbSession
from app.core.responses import ApiResponse
from ..auth.schemas import TokenRead
from ..auth.service import AuthService
from ..users.schemas import UserCreate, UserRead, UserSessionRead
from ..users.service import UserService


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=ApiResponse[UserRead],
    status_code=status.HTTP_201_CREATED,
)
async def register(data: UserCreate, session: DbSession):
    user = await UserService(session).register(data)

    return ApiResponse[UserRead](
        message="Usuario registrado correctamente.",
        data=UserRead.model_validate(user),
    )


@router.post("/login", response_model=TokenRead)
async def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: DbSession,
):
    token, user = await AuthService(session).login(
        identifier=form.username,
        password=form.password,
    )

    return TokenRead(
        access_token=token,
        user=UserSessionRead.from_user(user),
    )

