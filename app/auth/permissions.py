from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.auth.jwt_handler import decode_access_token
from app.core.exceptions import UnauthorizedException, ForbiddenException
from app.database.session import get_db
from app.models.user import User, UserRole

security_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Validate Bearer JWT and retrieve current authenticated user from database."""
    if not credentials:
        raise UnauthorizedException(detail="Authentication token is missing. Please provide a Bearer token.")

    token = credentials.credentials
    payload = decode_access_token(token)

    user_id: int | None = payload.get("sub")
    if user_id is None:
        raise UnauthorizedException(detail="Invalid token payload: missing subject identifier.")

    try:
        user_id_int = int(user_id)
    except (ValueError, TypeError):
        raise UnauthorizedException(detail="Invalid user identifier format in token.")

    user = db.query(User).filter(User.id == user_id_int).first()
    if not user:
        raise UnauthorizedException(detail="Authenticated user no longer exists in database.")

    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Dependency that restricts access exclusively to users with 'admin' role."""
    if current_user.role != UserRole.ADMIN.value:
        raise ForbiddenException(
            detail="Access forbidden: This action requires administrator privileges."
        )
    return current_user
