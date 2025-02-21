# app/schemas/log.py

from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class LogEntrySchema(BaseModel):
    id: int
    process_name: str
    start_time: datetime
    end_time: Optional[datetime]
    user_full_name: str
    result: str
    time_taken: Optional[str]
    time_taken_in_seconds: Optional[int]
    details: Optional[str]

    class Config:
        from_attributes = True
