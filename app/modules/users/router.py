from fastapi import APIRouter, Query
from typing import Annotated
from app.api.dependencies import DbSession
from app.core.responses import ApiResponse
from ..auth.dependencies import CurrentUser
from ..users.schemas import UserRead, UserUpdate, UserSessionRead
from ..users.service import UserService


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=ApiResponse[UserSessionRead])
async def get_me(user: CurrentUser):
    return ApiResponse[UserSessionRead](
        message="Usuario obtenido correctamente.",
        data=UserSessionRead.from_user(user),
    )


@router.patch("/me", response_model=ApiResponse[UserRead])
async def update_me(
    data: UserUpdate,
    user: CurrentUser,
    session: DbSession,
):
    updated_user = await UserService(session).update_me(user, data)

    return ApiResponse[UserRead](
        message="Usuario actualizado correctamente.",
        data=UserRead.model_validate(updated_user),
    )

@router.get("", response_model=ApiResponse[list[UserRead]])
async def list_users(
    session: DbSession,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    users = await UserService(session).list_users(
        offset,
        limit,
    )

    return ApiResponse[list[UserRead]](
        message="Usuarios obtenidos correctamente.",
        data=[
            UserRead.model_validate(user)
            for user in users
        ],
    )

