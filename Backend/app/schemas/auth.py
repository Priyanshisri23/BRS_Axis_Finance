from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    username: str
    is_active: bool
    is_superuser: bool

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class LoginCredentials(BaseModel):
    username: str
    password: str

class OTPVerification(BaseModel):
    username: str
    otp: str

class MFARequest(BaseModel):
    username: str
