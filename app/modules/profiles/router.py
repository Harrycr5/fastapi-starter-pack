from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.dependencies import DbSession
from app.core.pagination import Page, Pagination
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
    ProfilePermissionsRemove,
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
    response_model=ApiResponse[Page[ProfileRead]],
    dependencies=[Depends(require_permissions("profiles.read"))],
)
async def list_profiles(session: DbSession, pagination: Pagination):
    profiles, total = await ProfileService(session).list_profiles(
        pagination.offset, pagination.page_size
    )
    return ApiResponse[Page[ProfileRead]](
        message="Perfiles obtenidos correctamente.",
        data=Page[ProfileRead].build(
            [ProfileRead.model_validate(profile) for profile in profiles], total, pagination
        ),
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


@profiles_router.delete(
    "/{profile_id}/permissions",
    response_model=ApiResponse[ProfileDetailRead],
)
async def remove_profile_permissions(
    profile_id: UUID, data: ProfilePermissionsRemove, session: DbSession, admin: SuperAdmin
):
    profile = await ProfileService(session).remove_permissions(profile_id, data)
    return ApiResponse[ProfileDetailRead](
        message="Permisos retirados correctamente.",
        data=ProfileDetailRead.model_validate(profile),
    )


@permissions_router.get(
    "",
    response_model=ApiResponse[Page[PermissionRead]],
    dependencies=[Depends(require_permissions("permissions.read"))],
)
async def list_permissions(session: DbSession, pagination: Pagination):
    permissions, total = await ProfileService(session).list_permissions(
        pagination.offset, pagination.page_size
    )
    return ApiResponse[Page[PermissionRead]](
        message="Permisos obtenidos correctamente.",
        data=Page[PermissionRead].build(
            [PermissionRead.model_validate(permission) for permission in permissions],
            total,
            pagination,
        ),
    )


router.include_router(profiles_router)
router.include_router(permissions_router)
