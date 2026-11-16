from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..profiles.models import Profile
from ..users.models import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, user_id: UUID) -> User | None:
        statement = select(User).where(User.id == user_id)

        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email)

        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        statement = select(User).where(User.username == username)

        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_with_permissions(self, user_id: UUID) -> User | None:
        statement = (
            select(User)
            .where(User.id == user_id)
            .options(
                selectinload(User.profile).selectinload(
                    Profile.permissions
                )
            )
        )

        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        email: str,
        username: str,
        name: str,
        last_name: str,
        password_hash: str,
        profile_id: UUID,
    ) -> User:
        user = User(
            email=email,
            username=username,
            name=name,
            last_name=last_name,
            password_hash=password_hash,
            profile_id=profile_id,
        )

        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)

        return user
    
    async def update_personal_data(
        self,
        user: User,
        changes: dict[str, str],
    ) -> User:
        allowed_fields = {"name", "last_name"}

        if not changes.keys() <= allowed_fields:
            raise ValueError("Campos de actualización no permitidos.")

        for field, value in changes.items():
            setattr(user, field, value)

        await self.session.flush()
        await self.session.refresh(user)

        return user
    
    async def list_users(
        self,
        offset: int,
        limit: int,
    ) -> list[User]:
        statement = (
            select(User)
            .offset(offset)
            .limit(limit)
            .options(
                selectinload(User.profile).selectinload(
                    Profile.permissions
                )
            )
        )

        result = await self.session.execute(statement)
        return result.scalars().all()

