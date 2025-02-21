from app.db.base_class import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, VARCHAR


class ProcessData(Base):
    __tablename__ = 'Bot_Status'

    Sr_No = Column(Integer, primary_key=True, autoincrement=True)
    BotStart_Time = Column(DateTime, nullable=True)
    BotEnd_Time = Column(DateTime, nullable=True)
    ProcessName = Column(VARCHAR(500), nullable=True)
    TaskName = Column(VARCHAR(500), nullable=True)
    ApplicationName = Column(VARCHAR(500), nullable=True)
    LoginUserID = Column(VARCHAR(500), nullable=True)
    Status = Column(VARCHAR(500), nullable=True)
    Description = Column(VARCHAR(500), nullable=True)
    RunID = Column(Integer, nullable=True)
    ProcessID = Column(VARCHAR(500), nullable=True)