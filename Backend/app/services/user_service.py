from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session, aliased

from app.models.user import User as UserModel
from app.services.ldap_service import get_ldap_user_info
from app.utils.email_utils import send_email


def create_or_update_user(db: Session, username: str):
    """
    Create a new user in the database if they do not exist.
    Otherwise, update their details from LDAP.
    """
    # Fetch user details from LDAP
    ldap_user_info = get_ldap_user_info(username)
    if not ldap_user_info:
        raise HTTPException(status_code=404, detail="User not found in LDAP.")

    # Check if user exists
    db_user = db.query(UserModel).filter(UserModel.username == username).first()

    first_name = ldap_user_info.get("givenName") or ldap_user_info.get("cn", "").split()[0]
    last_name = ldap_user_info.get("sn", "")
    email = ldap_user_info.get("mail", "")

    if not email:
        raise HTTPException(status_code=400, detail="Email not found in LDAP.")

    if not db_user:
        # Insert new user with `is_active=False`
        new_user = UserModel(
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=username,
            ldap_dn=ldap_user_info["dn"],
            is_active=False,  # Require admin activation
            created_on=datetime.utcnow()
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    else:
        # Update details from LDAP
        db_user.first_name = first_name
        db_user.last_name = last_name
        db_user.email = email
        db_user.updated_on = datetime.utcnow()

        db.commit()
        db.refresh(db_user)
        return db_user


def update_user_status(db: Session, user_id: int, is_active: bool, admin_id: int):
    """
    Superadmin can activate or deactivate a user.
    Other attributes cannot be updated manually.
    """
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found.")

    # Allow only `is_active` to be changed
    db_user.is_active = is_active
    db_user.updated_by = admin_id
    db_user.updated_on = datetime.utcnow()

    db.commit()
    db.refresh(db_user)
    return db_user


from sqlalchemy.orm import joinedload
from app.models.user import User as UserModel


def get_all_users(db: Session):
    """Fetch all users, including the full name of the user who last updated them."""

    updated_by_alias = aliased(UserModel)  # Alias for updated_by user

    users = (
        db.query(
            UserModel.id,
            UserModel.first_name,
            UserModel.last_name,
            UserModel.email,
            UserModel.username,
            UserModel.is_active,
            UserModel.is_superuser,
            UserModel.ldap_dn,
            UserModel.created_on,
            UserModel.updated_on,
            updated_by_alias.id.label("updated_by_id"),
            updated_by_alias.first_name.label("updated_by_first_name"),
            updated_by_alias.last_name.label("updated_by_last_name")
        )
        .outerjoin(updated_by_alias, updated_by_alias.id == UserModel.updated_by)  # Correct join
        .all()
    )

    # Construct response
    result = []
    for user in users:
        result.append({
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "username": user.username,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "ldap_dn": user.ldap_dn,
            "created_on": user.created_on,
            "updated_on": user.updated_on,
            "updated_by": {
                "id": user.updated_by_id,
                "full_name": f"{user.updated_by_first_name} {user.updated_by_last_name}"
                if user.updated_by_id else None,
            },
        })

    return result


def get_user_by_id(db: Session, user_id: int) -> UserModel:
    """Fetch a single user by their primary key ID."""
    return db.query(UserModel).filter(UserModel.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> UserModel:
    """Fetch a user by their username."""
    return db.query(UserModel).filter(UserModel.username == username).first()


def send_account_activation_email(to_email: str, full_name: str):
    """Notify user that their account has been activated."""
    email_body = f"""
    <html>
    <body>
        <p>Hi {full_name},</p>
        <p>Your account has been successfully activated. You can now log in using your corporate credentials.</p>
        <p>Regards,<br>Admin Team</p>
    </body>
    </html>
    """
    send_email(
        to_email=to_email,
        subject="Account Activation Notification",
        body=email_body
    )


def delete_user(db: Session, user_id: int):
    """
    Delete a user from the system safely.
    """
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found.")

    try:
        db.delete(db_user)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting user: {e}")
