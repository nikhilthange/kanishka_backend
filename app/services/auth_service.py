from sqlalchemy.orm import Session
from app.auth.jwt_handler import hash_password, verify_password, create_access_token
from app.core.exceptions import ConflictException, UnauthorizedException
from app.models.user import User
from app.schemas.user import UserRegister, UserLogin, TokenResponse, UserResponse


class AuthService:
    @staticmethod
    def register_user(db: Session, user_data: UserRegister) -> User:
        """Register a new user if the email is not already taken."""
        existing_user = db.query(User).filter(User.email == user_data.email.lower()).first()
        if existing_user:
            raise ConflictException(detail=f"Email '{user_data.email}' is already registered.")

        new_user = User(
            name=user_data.name.strip(),
            email=user_data.email.lower().strip(),
            password=hash_password(user_data.password),
            role=user_data.role.value,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    @staticmethod
    def authenticate_user(db: Session, credentials: UserLogin) -> TokenResponse:
        """Authenticate user by email and password, returning a JWT token."""
        user = db.query(User).filter(User.email == credentials.email.lower().strip()).first()
        if not user or not verify_password(credentials.password, user.password):
            raise UnauthorizedException(detail="Invalid email or password.")

        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "email": user.email,
                "role": user.role,
            }
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse.model_validate(user),
        )
