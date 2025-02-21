from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.services.ldap_service import ldap_authenticate_user, get_ldap_user_info
from app.models.user import User as UserModel
from app.core.security import create_access_token


def authenticate_user(db: Session, username: str, password: str):
    """
    Authenticate user via LDAP.
    If the user is found in LDAP but not in DB, insert them as inactive.
    """
    ldap_authenticated = ldap_authenticate_user(username, password)
    if not ldap_authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password."
        )

    # Check if user exists in DB
    db_user = db.query(UserModel).filter(UserModel.username == username).first()

    if not db_user:
        # Fetch user details from LDAP
        ldap_user_info = get_ldap_user_info(username)

        # If no email is found, prevent user creation
        if not ldap_user_info or not ldap_user_info.get("email"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Your account does not have a registered email. Please contact the administrator."
            )

        # Insert new user as inactive
        new_user = UserModel(
            first_name=ldap_user_info["first_name"],
            last_name=ldap_user_info["last_name"],
            email=ldap_user_info["email"],
            username=username,
            ldap_dn=ldap_user_info["dn"],
            is_active=False  # Default new users to inactive
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been created but is inactive. Please contact the admin."
        )

    if not db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is inactive. Contact the administrator."
        )

    # Generate JWT Token
    access_token = create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}
