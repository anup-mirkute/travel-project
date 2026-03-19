from pydantic import BaseModel, EmailStr, field_validator, ConfigDict, model_validator
from typing import Optional
import re


class UserCustomerCreateSchema(BaseModel):
    username: Optional[str] = None
    email: EmailStr
    password: str
    name: Optional[str] = None
    phone_no: Optional[str] = None
    is_active: Optional[bool] = None
    is_email_verified: Optional[bool] = None
    is_phone_no_verified: Optional[bool] = None

    # Trim all string fields
    @field_validator("*", mode="before")
    @classmethod
    def trim_strings(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        if v is None:
            return v
        if not re.fullmatch(r"^[a-z0-9_]+$", v.lower()):
            raise ValueError("Username must be lowercase letters, numbers, and underscores only")
        return v.lower()

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if v is None:
            return v
        if not re.fullmatch(r"[A-Za-z\s]+", v):
            raise ValueError("Name must contain only letters and spaces")
        return v.title()

    @field_validator("phone_no")
    @classmethod
    def validate_phone_no(cls, v):
        if v is None:
            return v
        pattern = r"^\+?[1-9]\d{9,14}$"
        if not re.fullmatch(pattern, v):
            raise ValueError("Invalid phone number format")
        return v


class UserCustomerLoginSchema(BaseModel):
    email: EmailStr
    password: str

    # Trim all string fields
    @field_validator("*", mode="before")
    @classmethod
    def trim_strings(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v


class UserCustomerLogoutSchema(BaseModel):
    refresh_token: str


class UserCustomerOTPSchema(BaseModel):
    user_id : str
    username: str 
    email: EmailStr
    otp : Optional[str] = None
    otp_type : str


class ForgotPasswordRequestSchema(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
 
    @field_validator("*", mode="before")
    @classmethod
    def trim_strings(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v
 
    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        if v is None:
            return v
        if not re.fullmatch(r"^[a-z0-9_]+$", v.lower()):
            raise ValueError("Username must be lowercase letters, numbers, and underscores only")
        return v.lower()
 
    @model_validator(mode="after")
    def require_email_or_username(self):
        if not self.email and not self.username:
            raise ValueError("Either email or username must be provided")
        return self
 
 
class ForgotPasswordUpdateSchema(BaseModel):
    user_id: str
    otp: str
    new_password: str
    confirm_password: str
 
    @field_validator("*", mode="before")
    @classmethod
    def trim_strings(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v
 
    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        return v
 
    @model_validator(mode="after")
    def passwords_must_match(self):
        if self.new_password != self.confirm_password:
            raise ValueError("new_password and confirm_password do not match")
        return self