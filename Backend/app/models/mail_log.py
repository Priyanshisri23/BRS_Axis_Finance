from app.db.base_class import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, VARCHAR


class MailLog(Base):
    __tablename__ = 'Bot_DetailLog'

    Sr_No = Column(Integer, primary_key=True, autoincrement=True)
    Timestamp = Column(DateTime, nullable=True)
    RunID = Column(Integer, nullable=True)
    SystemUsername = Column(VARCHAR(500), nullable=True)
    MachineName = Column(VARCHAR(500), nullable=True)
    ProcessName = Column(VARCHAR(500), nullable=True)
    TaskName = Column(VARCHAR(500), nullable=True)
    ApplicationName = Column(VARCHAR(500), nullable=True)
    LoginUserID = Column(VARCHAR(500), nullable=True)
    RecorderIdentifier = Column(VARCHAR(500), nullable=True)
    Description = Column(VARCHAR(500), nullable=True)
    LogLevel = Column(VARCHAR(500), nullable=True)
    cpuusage_percentage = Column(Integer, nullable=True, name="CPUUsage(%)")
    ramusage_mb = Column(Integer, nullable=True, name="RAMUsage(MB)")
    ProcessID = Column(VARCHAR(500), nullable=True)