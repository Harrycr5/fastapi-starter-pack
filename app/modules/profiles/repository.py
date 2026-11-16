from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.profiles.models import profile_permissions

from .models import Permission, Profile


class ProfileRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_code(self, code: str) -> Profile | None:
        result = await self.session.execute(select(Profile).where(Profile.code == code))
        return result.scalar_one_or_none()

    async def get_by_id(self, profile_id: UUID) -> Profile | None:
        result = await self.session.execute(
            select(Profile)
            .where(Profile.id == profile_id)
            .options(selectinload(Profile.permissions))
            .execution_options(populate_existing=True)
        )
        return result.scalar_one_or_none()

    async def list_profiles(
        self,
        offset: int,
        limit: int,
    ) -> list[Profile]:
        result = await self.session.execute(
            select(Profile).order_by(Profile.code).offset(offset).limit(limit)
        )
        return list(result.scalars().all())

    async def list_permissions(
        self,
        offset: int,
        limit: int,
    ) -> list[Permission]:
        result = await self.session.execute(
            select(Permission).order_by(Permission.code).offset(offset).limit(limit)
        )
        return list(result.scalars().all())

    async def get_permissions_by_ids(
        self,
        permission_ids: set[UUID],
    ) -> list[Permission]:
        if not permission_ids:
            return []

        result = await self.session.execute(
            select(Permission).where(Permission.id.in_(permission_ids)).order_by(Permission.code)
        )
        return list(result.scalars().all())

    async def create_profile(
        self,
        *,
        code: str,
        name: str,
        description: str | None,
    ) -> Profile:
        profile = Profile(
            code=code,
            name=name,
            description=description,
            permissions=[],
        )
        self.session.add(profile)

        await self.session.flush()
        await self.session.refresh(profile)

        return profile

    async def add_permissions(
        self,
        profile_id: UUID,
        permission_ids: set[UUID],
    ) -> None:
        if not permission_ids:
            return

        statement = (
            insert(profile_permissions)
            .values(
                [
                    {
                        "profile_id": profile_id,
                        "permission_id": permission_id,
                    }
                    for permission_id in permission_ids
                ]
            )
            .on_conflict_do_nothing(index_elements=["profile_id", "permission_id"])
        )

        await self.session.execute(statement)

    async def remove_permissions(self, profile_id: UUID, permission_ids: set[UUID]) -> None:
        if permission_ids:
            await self.session.execute(
                delete(profile_permissions).where(
                    profile_permissions.c.profile_id == profile_id,
                    profile_permissions.c.permission_id.in_(permission_ids),
                )
            )

    async def count_profiles(self) -> int:
        return await self.session.scalar(select(func.count()).select_from(Profile)) or 0

    async def count_permissions(self) -> int:
        return await self.session.scalar(select(func.count()).select_from(Permission)) or 0
