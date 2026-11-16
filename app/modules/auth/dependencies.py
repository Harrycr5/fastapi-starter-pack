from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError

from app.api.dependencies import DbSession
from app.core.security import decode_access_token
from ..users.models import User
from ..users.repository import UserRepository


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: DbSession,
) -> User:
    try:
        user_id = decode_access_token(token)
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o vencido.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    repository = UserRepository(session)
    user = await repository.get_with_permissions(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active or not user.profile.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario o perfil desactivado.",
        )

    return user

def require_permissions(*required_codes: str):
    async def check_permissions(user: CurrentUser) -> User:
        # Perfil reservado: acceso completo, también a permisos futuros.
        if user.profile.code == "superadmin":
            return user

        available_codes = {
            permission.code
            for permission in user.profile.permissions
        }

        if not set(required_codes).issubset(available_codes):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para esta operación.",
            )

        return user

    return check_permissions


CurrentUser = Annotated[User, Depends(get_current_user)]

async def require_superadmin(user: CurrentUser) -> User:
    if user.profile.code != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta operación requiere ser superadmin.",
        )

    return user


SuperAdmin = Annotated[User, Depends(require_superadmin)]

