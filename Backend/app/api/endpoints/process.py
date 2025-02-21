# app/api/endpoints/process.py

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_authenticated_user, get_current_user_email
from app.models.log import Log
from app.process.account_607 import main_account_607
from app.process.account_669 import main_account_669
from app.process.account_7687 import main_account_7687
from app.process.account_8350 import main_account_8350
from app.process.account_9197 import main_account_9197
from app.process.account_86033 import main_account_86033

router = APIRouter()


def log_bot_process(db: Session, user_id: int, process_name: str, result: str, details: str, start_time: datetime,
                    end_time: datetime = None):
    """Helper function to log bot processes."""
    time_taken = None
    if start_time and end_time:
        time_taken = str((end_time - start_time).total_seconds()) + " seconds"

    log_entry = Log(
        user_id=user_id,
        process_name=process_name,
        start_time=start_time,
        end_time=end_time,
        result=result,
        details=details,
    )
    db.add(log_entry)
    db.commit()

#############  ACCOUNT 607  #############

@router.post("/account_607")
async def account_1(
        user_email: str = Depends(get_current_user_email),
        current_user=Depends(get_authenticated_user),
        db: Session = Depends(get_db)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    start_time = datetime.utcnow()

    try:
        # Execute Account 607

        result, status = main_account_607(to_email=user_email)

        # Calculate the end time
        end_time = datetime.utcnow()

        # Log the process and store time taken
        log_bot_process(db, current_user.id, "BRS - Account 607", status, result, start_time, end_time)

        # Return success message
        return {"success": True, "result": result, "status": status}

    except Exception as e:
        end_time = datetime.utcnow()
        # Log the exception
        log_bot_process(db, current_user.id, "BRS - Account 607", "Failure", str(e), start_time, end_time)
        return {"success": False, "error": str(e)}


#############  ACCOUNT 669  #############

@router.post("/account_669")
async def account_1(
        user_email: str = Depends(get_current_user_email),
        current_user=Depends(get_authenticated_user),
        db: Session = Depends(get_db)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    start_time = datetime.utcnow()

    try:

        result, status = main_account_669(to_email=user_email)

        # Calculate the end time
        end_time = datetime.utcnow()

        # Log the process and store time taken
        log_bot_process(db, current_user.id, "BRS - Account 669", status, result, start_time, end_time)

        # Return success message
        return {"success": True, "result": result, "status": status}

    except Exception as e:
        end_time = datetime.utcnow()
        # Log the exception
        log_bot_process(db, current_user.id, "BRS - Account 669", "Failure", str(e), start_time, end_time)
        return {"success": False, "error": str(e)}


#############  ACCOUNT 7687  #############

@router.post("/account_7687")
async def account_1(
        user_email: str = Depends(get_current_user_email),
        current_user=Depends(get_authenticated_user),
        db: Session = Depends(get_db)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    start_time = datetime.utcnow()

    try:

        result, status = main_account_7687(to_email=user_email)

        # Calculate the end time
        end_time = datetime.utcnow()

        # Log the process and store time taken
        log_bot_process(db, current_user.id, "BRS - Account 7687", status, result, start_time, end_time)

        # Return success message
        return {"success": True, "result": result, "status": status}

    except Exception as e:
        end_time = datetime.utcnow()
        # Log the exception
        log_bot_process(db, current_user.id, "BRS - Account 7687", "Failure", str(e), start_time, end_time)
        return {"success": False, "error": str(e)}

#############  ACCOUNT 8350  #############

@router.post("/account_8350")
async def account_1(
        user_email: str = Depends(get_current_user_email),
        current_user=Depends(get_authenticated_user),
        db: Session = Depends(get_db)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    start_time = datetime.utcnow()

    try:

        result, status = main_account_8350(to_email=user_email)

        # Calculate the end time
        end_time = datetime.utcnow()

        # Log the process and store time taken
        log_bot_process(db, current_user.id, "BRS - Account 8350", status, result, start_time, end_time)

        # Return success message
        return {"success": True, "result": result, "status": status}

    except Exception as e:
        end_time = datetime.utcnow()
        # Log the exception
        log_bot_process(db, current_user.id, "BRS - Account 8350", "Failure", str(e), start_time, end_time)
        return {"success": False, "error": str(e)}


#############  ACCOUNT 9197  #############

@router.post("/account_9197")
async def account_1(
        user_email: str = Depends(get_current_user_email),
        current_user=Depends(get_authenticated_user),
        db: Session = Depends(get_db)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    start_time = datetime.utcnow()

    try:

        result, status = main_account_9197(to_email=user_email)

        # Calculate the end time
        end_time = datetime.utcnow()

        # Log the process and store time taken
        log_bot_process(db, current_user.id, "BRS - Account 9197", status, result, start_time, end_time)

        # Return success message
        return {"success": True, "result": result, "status": status}

    except Exception as e:
        end_time = datetime.utcnow()
        # Log the exception
        log_bot_process(db, current_user.id, "BRS - Account 9197", "Failure", str(e), start_time, end_time)
        return {"success": False, "error": str(e)}

#############  ACCOUNT 86033  #############

@router.post("/account_86033")
async def account_1(
        user_email: str = Depends(get_current_user_email),
        current_user=Depends(get_authenticated_user),
        db: Session = Depends(get_db)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    start_time = datetime.utcnow()

    try:

        result, status = main_account_86033(to_email=user_email)

        # Calculate the end time
        end_time = datetime.utcnow()

        # Log the process and store time taken
        log_bot_process(db, current_user.id, "BRS - Account 86033", status, result, start_time, end_time)

        # Return success message
        return {"success": True, "result": result, "status": status}

    except Exception as e:
        end_time = datetime.utcnow()
        # Log the exception
        log_bot_process(db, current_user.id, "BRS - Account 86033", "Failure", str(e), start_time, end_time)
        return {"success": False, "error": str(e)}

