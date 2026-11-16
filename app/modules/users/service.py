from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from ..profiles.repository import ProfileRepository
from ..users.exceptions import (
    RegistrationUnavailableError,
    UserAlreadyExistsError,
)
from ..users.models import User
from ..users.repository import UserRepository
from ..users.schemas import UserCreate, UserUpdate


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.users = UserRepository(session)
        self.profiles = ProfileRepository(session)

    async def register(self, data: UserCreate) -> User:
        email = str(data.email).lower()
        username = data.username.lower()

        if await self.users.get_by_email(email):
            raise UserAlreadyExistsError(
                "El correo ya está registrado."
            )

        if await self.users.get_by_username(username):
            raise UserAlreadyExistsError(
                "El nombre de usuario ya está registrado."
            )

        profile = await self.profiles.get_by_code("user")

        if profile is None or not profile.is_active:
            raise RegistrationUnavailableError(
                "El registro de usuarios no está disponible."
            )

        password_hash = await hash_password(
            data.password.get_secret_value()
        )

        try:
            user = await self.users.create(
                email=email,
                username=username,
                name=data.name,
                last_name=data.last_name,
                password_hash=password_hash,
                profile_id=profile.id,
            )

            await self.session.commit()

        except IntegrityError as exc:
            await self.session.rollback()

            if getattr(exc.orig, "sqlstate", None) == "23505":
                raise UserAlreadyExistsError(
                    "El correo o el nombre de usuario ya está registrado."
                ) from exc

            raise

        return user
    
    async def update_me(
        self,
        user: User,
        data: UserUpdate,
    ) -> User:
        changes = data.model_dump(exclude_unset=True)

        try:
            user = await self.users.update_personal_data(
                user,
                changes,
            )
            await self.session.commit()

        except Exception:
            await self.session.rollback()
            raise

        return user
    
    async def list_users(
        self,
        offset: int,
        limit: int,
    ) -> list[User]:
        return await self.users.list_users(offset, limit)
    
