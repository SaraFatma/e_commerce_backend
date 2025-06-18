from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from app.auth.models import RoleEnum
import re

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: RoleEnum = RoleEnum.user # default role

    @validator("email")
    def validate_gmail(cls, value):
        pattern = r"^[a-zA-Z][a-zA-Z0-9]*@gmail\.com$"
        if not re.match(pattern, value):
            raise ValueError("Email must be a valid Gmail address, starting with a letter, with no special characters.")
        return value


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):# jwt token generate krne ke baad client ko bhejne ke liye
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):# intenal authorzation me..data token ko decode krne ke bad milta hai
    email: Optional[str] = None
    role: Optional[str] = None

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: RoleEnum

    class Config:
        orm_mode = True

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


