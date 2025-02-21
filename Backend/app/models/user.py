from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(150), nullable=False)
    last_name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    username = Column(String(150), unique=True, index=True, nullable=False)
    ldap_dn = Column(String, nullable=True)  # Store the LDAP Distinguished Name
    is_active = Column(Boolean, default=False)  # New users will be inactive
    is_superuser = Column(Boolean, default=False)

    # Audit fields
    created_on = Column(DateTime(timezone=True), server_default=func.now())
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    updated_by_user = relationship("User", foreign_keys=[updated_by], remote_side=[id])
    logs = relationship("Log", back_populates="user", lazy="joined")
