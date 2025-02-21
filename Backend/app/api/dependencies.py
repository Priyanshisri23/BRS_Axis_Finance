# app/api/dependencies.py

from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.db_engine import SessionLocal
from app.core.security import create_access_token, verify_token_and_get_user
from app.models.user import User as UserModel
from app.services.ldap_service import ldap_authenticate_user, get_ldap_user_info
from app.services.user_service import create_or_update_user, get_user_by_username
from datetime import timedelta
from app.core.config import config

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_db() -> Generator:
    """Yield a new DB session per request."""
    try:
        db = SessionLocal
        yield db
    finally:
        db.close()


async def get_authenticated_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> UserModel:
    """
    Authenticate user using JWT token after initial LDAP authentication.
    """
    user = verify_token_and_get_user(db, token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> UserModel:
    """
    Retrieve the currently authenticated user using JWT.
    """
    user = verify_token_and_get_user(db, token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user


def require_superuser(
    current_user: UserModel = Depends(get_current_user)
) -> UserModel:
    """Only allow superuser to proceed."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized; user is not a superuser."
        )
    return current_user


def get_current_user_email(
    current_user: UserModel = Depends(get_current_user)
) -> str:
    """
    Retrieve the email of the currently authenticated user.
    """
    if not current_user.email:
        raise HTTPException(
            status_code=400,
            detail="Authenticated user does not have a valid email address."
        )
    return current_user.email


def authenticate_user(username: str, password: str, db: Session) -> dict:
    """
    Authenticate user using LDAP.
    - If user exists in LDAP but not in DB → insert as inactive.
    - If user is inactive → deny access.
    - If authenticated → return user and generate JWT.
    """
    ldap_user = ldap_authenticate_user(username, password)

    if not ldap_user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    db_user = get_user_by_username(db, username)

    if not db_user:
        # Create or update user with **is_active=False**
        db_user = create_or_update_user(db, username)

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been created but is inactive. Contact the administrator."
        )

    if not db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive. Contact the administrator."
        )

    # Generate JWT token after successful authentication
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}
