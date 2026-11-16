from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies import DbSession
from app.core.responses import ApiResponse
from app.modules.auth.dependencies import CurrentSession
from app.modules.auth.schemas import RefreshRequest, TokenRead
from app.modules.auth.service import AuthService
from app.modules.users.schemas import UserCreate, UserRead
from app.modules.users.service import UserService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=ApiResponse[UserRead], status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate, session: DbSession):
    user = await UserService(session).register(data)
    return ApiResponse[UserRead](
        message="Usuario registrado correctamente.", data=UserRead.model_validate(user)
    )


@router.post("/login", response_model=TokenRead)
async def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], session: DbSession):
    return await AuthService(session).login(form.username, form.password)


@router.post("/refresh", response_model=TokenRead)
async def refresh(data: RefreshRequest, session: DbSession):
    return await AuthService(session).refresh(data.refresh_token.get_secret_value())


@router.post("/logout", response_model=ApiResponse[None])
async def logout(auth_session: CurrentSession, session: DbSession):
    await AuthService(session).logout(auth_session)
    return ApiResponse[None](message="Sesión cerrada correctamente.", data=None)
