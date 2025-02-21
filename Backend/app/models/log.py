# app/models/log.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime
import pytz

class Log(Base):
    __tablename__ = 'logs'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    process_name = Column(String, nullable=False)
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=True)
    result = Column(String, nullable=False, default="Pending")
    details = Column(String, nullable=True)

    user = relationship("User", back_populates="logs", lazy="selectin")

    # def calculate_time_taken(self):
    #     """Calculate time taken for the process in seconds."""
    #     if self.start_time and self.end_time:
    #         print(f"Start time: {self.start_time} and End Time: {self.end_time}")
    #         print(f"Type of - Start time: {type(self.start_time)} and End Time: {type(self.end_time)}")
            
    #         start_time = self.start_time.astimezone()
    #         end_time = self.end_time.astimezone()
    #         total_seconds = (end_time - start_time).total_seconds()
    #         print(f"total seconds: {total_seconds}")
    #         return total_seconds


    def calculate_time_taken(self):
        """Calculate time taken for the process in seconds."""
        try:

            if self.start_time and self.end_time:
                # print(f"Start time: {self.start_time} and End Time: {self.end_time}")
                # print(f"Type of - Start time: {type(self.start_time)} and End Time: {type(self.end_time)}")
                
                start_time = self.start_time if isinstance(self.start_time, datetime) else datetime.fromisoformat(self.start_time)
                end_time = self.start_time if isinstance(self.end_time, datetime) else datetime.fromisoformat(self.start_time)
                
                print(f"Start time: {self.start_time} and End Time: {self.end_time}")
                print(f"Type of - Start time: {type(self.start_time)} and End Time: {type(self.end_time)}")
                
                total_seconds = (end_time - start_time).total_seconds()
                print(f"total seconds: {total_seconds}")
                return total_seconds

        except Exception as e:
            print(f"Error Occured: {e}")
    
        return None
