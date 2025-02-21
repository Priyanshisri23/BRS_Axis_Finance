from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.schemas.auth import Token, LoginCredentials, UserBase
from app.services.auth_service import authenticate_user
from app.api.dependencies import get_db, get_authenticated_user
from app.models.user import User as UserModel

router = APIRouter()

@router.get("/me", response_model=UserBase)
def get_logged_in_user(current_user: UserModel = Depends(get_authenticated_user)):
    """Retrieve details of the logged-in user."""
    return {
        "username": current_user.username,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "email": current_user.email,
        "is_active": current_user.is_active,
        "is_superuser": current_user.is_superuser
    }

@router.post("/login", response_model=Token)
def login(credentials: LoginCredentials, db: Session = Depends(get_db)):
    """
    Authenticate user via LDAP and return JWT token.
    """
    try:
        auth_result = authenticate_user(db, credentials.username, credentials.password)
        return auth_result
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
