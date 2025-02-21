# app/api/endpoints/bots.py

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.dependencies import get_db, get_authenticated_user
from app.models.log import Log
from app.models.user import User as UserModel
from app.services.bot_services import BotService

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


@router.post("/bot1")
async def run_bot1(
        current_user=Depends(get_authenticated_user),
        db: Session = Depends(get_db)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    start_time = datetime.utcnow()

    try:
        # Execute the bot1 process
        result, status = BotService.run_bot1()
        end_time = datetime.utcnow()

        # Log the process and store time taken
        log_bot_process(db, current_user.id, "Bot 1", status, result, start_time, end_time)

        # Return success message
        return {"success": True, "result": result, "status": status}

    except Exception as e:
        end_time = datetime.utcnow()
        # Log the exception
        log_bot_process(db, current_user.id, "Bot 1", "Failure", str(e), start_time, end_time)
        return {"success": False, "error": str(e)}


@router.post("/bot2")
async def run_bot2(
        current_user=Depends(get_authenticated_user),
        db: Session = Depends(get_db)
):
    start_time = datetime.utcnow()

    try:
        # Execute the bot2 process
        result, status = BotService.run_bot2()
        end_time = datetime.utcnow()

        # Log the process and store time taken
        log_bot_process(db, current_user.id, "Bot 2", status, result, start_time, end_time)

        return {"success": True, "result": result, "status": status}

    except Exception as e:
        end_time = datetime.utcnow()
        # Log the exception
        log_bot_process(db, current_user.id, "Bot 2", "Failure", str(e), start_time, end_time)
        return {"success": False, "error": str(e)}


@router.post("/bot3")
async def run_bot3(
        current_user=Depends(get_authenticated_user),
        db: Session = Depends(get_db)
):
    start_time = datetime.utcnow()

    try:
        # Execute the bot3 process
        result, status = BotService.run_bot3()
        end_time = datetime.utcnow()

        # Log the process and store time taken
        log_bot_process(db, current_user.id, "Bot 3", status, result, start_time, end_time)

        return {"success": True, "result": result, "status": status}

    except Exception as e:
        end_time = datetime.utcnow()
        # Log the exception
        log_bot_process(db, current_user.id, "Bot 3", "Failure", str(e), start_time, end_time)
        return {"success": False, "error": str(e)}


@router.post("/bot4")
async def run_bot4(
        current_user=Depends(get_authenticated_user),
        db: Session = Depends(get_db)
):
    start_time = datetime.utcnow()

    try:
        # Execute the bot4 process
        result, status = BotService.run_bot4()
        end_time = datetime.utcnow()

        # Log the process and store time taken
        log_bot_process(db, current_user.id, "Bot 4", status, result, start_time, end_time)

        return {"success": True, "result": result, "status": status}

    except Exception as e:
        end_time = datetime.utcnow()
        # Log the exception
        log_bot_process(db, current_user.id, "Bot 4", "Failure", str(e), start_time, end_time)
        return {"success": False, "error": str(e)}
