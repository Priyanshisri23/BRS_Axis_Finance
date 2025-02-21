from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.dependencies import get_db, get_authenticated_user
from app.models.log import Log
from app.schemas.log import LogEntrySchema
from app.utils.custom_logger import logger
import pytz
from datetime import datetime

router = APIRouter()


def format_time_taken(seconds: float):
    """Formats time taken in a human-readable form."""
    seconds = round(seconds)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"


@router.get("/logs", response_model=List[LogEntrySchema])
def get_logs(current_user=Depends(get_authenticated_user), db: Session = Depends(get_db)):
    """
    Fetch logs of bot processes. Restricted to authenticated users.
    """
    logs = db.query(Log).order_by(Log.id.desc()).all()
    logger.info(f"Fetched {len(logs)} logs")

    if not logs:
        return []

    log_entries = []
    for log in logs:
        user_full_name = f"{log.user.first_name} {log.user.last_name}" if log.user else "Unknown User"

        time_taken_in_seconds = log.calculate_time_taken()

        start_time = (
            log.start_time if isinstance(log.start_time, datetime) else datetime.fromisoformat(log.start_time) if log.start_time else None
        )
        end_time = (
            log.start_time if isinstance(log.end_time, datetime) else datetime.fromisoformat(log.end_time) if log.end_time else None
        )

        # start_time_ist = log.start_time.astimezone(pytz.timezone('Asia/Kolkata')) if log.start_time else None


        # end_time_ist = log.end_time.astimezone(pytz.timezone('Asia/Kolkata')) if log.end_time else None

        log_entries.append({
            "id": log.id,
            "process_name": log.process_name,
            "start_time": start_time or "N/A",
            "end_time": end_time or "N/A",
            "user_full_name": user_full_name,
            "result": log.result or 'Unknown',
            "time_taken": format_time_taken(time_taken_in_seconds) if time_taken_in_seconds else 'N/A',
            "time_taken_in_seconds": int(time_taken_in_seconds) if time_taken_in_seconds else None,
            "details": log.details or "No details available"
        })


    return log_entries
