from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    DUMMY_PASSWORD_HASH,
    create_access_token,
    verify_password,
)
from ..auth.exceptions import InvalidCredentialsError
from ..users.repository import UserRepository
from ..users.models import User

class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.users = UserRepository(session)

    async def login(self, identifier: str, password: str) -> tuple[str, User]:
        identifier = identifier.strip().lower()

        if "@" in identifier:
            user = await self.users.get_by_email(identifier)
        else:
            user = await self.users.get_by_username(identifier)

        password_hash = (
            user.password_hash
            if user is not None
            else DUMMY_PASSWORD_HASH
        )

        valid_password = await verify_password(
            password,
            password_hash,
        )

        if user is None or not valid_password:
            raise InvalidCredentialsError()

        # Carga explícitamente perfil y permisos.
        user = await self.users.get_with_permissions(user.id)

        if (
            user is None
            or not user.is_active
            or not user.profile.is_active
        ):
            raise InvalidCredentialsError()

        return create_access_token(user.id), user

