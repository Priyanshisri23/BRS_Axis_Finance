from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator

class UserStatusUpdate(BaseModel):
    is_active: bool


class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    username: str
    is_active: bool

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    username: str
    is_active: bool = False  # New users are inactive until approved
    ldap_dn: Optional[str] = None  # Store LDAP DN


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    is_active: Optional[bool] = None


# # ✅ Fix: Add `updated_by` field to UserOut Schema
# class UserOut(UserBase):
#     id: int
#     is_superuser: bool
#     ldap_dn: Optional[str]
#     created_on: Optional[datetime]
#     updated_on: Optional[datetime]
#     updated_by: Optional[dict] = None  # ✅ Include updated_by field in response


class UserOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    username: str
    is_active: bool
    is_superuser: bool
    ldap_dn: Optional[str]
    created_on: Optional[datetime]
    updated_on: Optional[datetime]

    @field_validator("created_on", "updated_on", mode="before")
    @classmethod
    def parse_datetime(cls, value):
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace(" +00:00", ""))

            except:
                pass

        return value
    
    class Config:
        from_attributes = True