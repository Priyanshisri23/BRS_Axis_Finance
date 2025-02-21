# app/api/endpoints/user_management.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, require_superuser
from app.schemas.user import UserOut, UserStatusUpdate
from app.services.user_service import (
    get_user_by_id,
    update_user_status,
    get_all_users,
    delete_user,
)
from app.utils.email_utils import send_email

router = APIRouter()


@router.get("/", response_model=list[UserOut])
def list_users(
        db: Session = Depends(get_db),
        _superuser=Depends(require_superuser),
):
    """
    List all users with updated_by full name.
    Only accessible by superuser.
    """
    return get_all_users(db)


@router.put("/{user_id}/update-status")
def update_user_status_endpoint(
        user_id: int,
        status_update: UserStatusUpdate,  # JSON Body
        db: Session = Depends(get_db),
        current_user=Depends(require_superuser),
):
    """
    Superadmin can activate or deactivate a user.
    Other attributes cannot be updated manually.
    """

    db_user = get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found.")

    # 🚀 Prevent user from deactivating themselves
    if current_user.id == user_id and not status_update.is_active:
        raise HTTPException(
            status_code=400,
            detail="You cannot deactivate your own account."
        )

    updated_user = update_user_status(db, user_id, status_update.is_active, current_user.id)

    # Send email notification
    email_body = f"""
    <html>
    <body>
        <p>Hi {updated_user.first_name} {updated_user.last_name},</p>
        <p>Your account status has been updated by the Admin.</p>
        <p><strong>New Status:</strong> {"Active" if status_update.is_active else "Inactive"}</p>
        <p>Regards,<br>Admin Team</p>
    </body>
    </html>
    """
    send_email(
        to_email=updated_user.email,
        subject="Account Status Updated",
        body=email_body
    )

    return {"message": f"User '{updated_user.username}' is now {'Active' if status_update.is_active else 'Inactive'}."}


@router.delete("/{user_id}")
def delete_user_endpoint(
        user_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(require_superuser),
):
    """
    Delete a user by their ID.
    Only accessible by superuser.
    """
    # Fetch user from DB
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found.")

    # 🚀 Prevent self-deletion
    if current_user.id == user_id:
        raise HTTPException(
            status_code=400,
            detail="You cannot delete your own account."
        )

    # Delete user and associated logs
    delete_user(db, user_id)

    return {"message": f"User '{db_user.username}' and their logs have been successfully deleted."}
