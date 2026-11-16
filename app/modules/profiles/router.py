from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies import DbSession
from app.core.responses import ApiResponse
from app.modules.auth.dependencies import (
    SuperAdmin,
    require_permissions,
)
from .schemas import (
    PermissionRead,
    ProfileCreate,
    ProfileDetailRead,
    ProfilePermissionsAdd,
    ProfileRead,
)
from .service import ProfileService


router = APIRouter()

profiles_router = APIRouter(
    prefix="/profiles",
    tags=["Profiles"],
)

permissions_router = APIRouter(
    prefix="/permissions",
    tags=["Permissions"],
)


@profiles_router.get(
    "",
    response_model=ApiResponse[list[ProfileRead]],
    dependencies=[Depends(require_permissions("profiles.read"))],
)
async def list_profiles(
    session: DbSession,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    profiles = await ProfileService(session).list_profiles(
        offset,
        limit,
    )

    return ApiResponse[list[ProfileRead]](
        message="Perfiles obtenidos correctamente.",
        data=[
            ProfileRead.model_validate(profile)
            for profile in profiles
        ],
    )


@profiles_router.get(
    "/{profile_id}",
    response_model=ApiResponse[ProfileDetailRead],
    dependencies=[Depends(require_permissions("profiles.read"))],
)
async def get_profile(profile_id: UUID, session: DbSession):
    profile = await ProfileService(session).get_profile(profile_id)

    return ApiResponse[ProfileDetailRead](
        message="Perfil obtenido correctamente.",
        data=ProfileDetailRead.model_validate(profile),
    )


@profiles_router.post(
    "",
    response_model=ApiResponse[ProfileRead],
    status_code=status.HTTP_201_CREATED,
)
async def create_profile(
    data: ProfileCreate,
    session: DbSession,
    admin: SuperAdmin,
):
    profile = await ProfileService(session).create_profile(data)

    return ApiResponse[ProfileRead](
        message="Perfil creado correctamente.",
        data=ProfileRead.model_validate(profile),
    )


@profiles_router.post(
    "/{profile_id}/permissions",
    response_model=ApiResponse[ProfileDetailRead],
)
async def add_profile_permissions(
    profile_id: UUID,
    data: ProfilePermissionsAdd,
    session: DbSession,
    admin: SuperAdmin,
):
    profile = await ProfileService(session).add_permissions(
        profile_id,
        data,
    )

    return ApiResponse[ProfileDetailRead](
        message="Permisos añadidos correctamente.",
        data=ProfileDetailRead.model_validate(profile),
    )


@permissions_router.get(
    "",
    response_model=ApiResponse[list[PermissionRead]],
    dependencies=[Depends(require_permissions("permissions.read"))],
)
async def list_permissions(
    session: DbSession,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    permissions = await ProfileService(session).list_permissions(
        offset,
        limit,
    )

    return ApiResponse[list[PermissionRead]](
        message="Permisos obtenidos correctamente.",
        data=[
            PermissionRead.model_validate(permission)
            for permission in permissions
        ],
    )


router.include_router(profiles_router)
router.include_router(permissions_router)

