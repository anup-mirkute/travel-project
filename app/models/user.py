from sqlalchemy import Column, Integer, String, DateTime, func, Boolean, ForeignKey
from core.database import Base
from datetime import datetime, timedelta, timezone
import uuid
import re
from pydantic import validator
from core.utils import current_dtts
from core.config import settings

def generate_customer_id():
    year = datetime.now().year
    month = datetime.now().month
    random_part = uuid.uuid4().hex[:6].upper()
    return f"CUST-{random_part}-{month:02d}{year}"

def otp_expiry_time():
    return current_dtts() + timedelta(minutes=settings.EMAIL_VERIFY_EXPIRE_MINUTES)

class UserCustomerModel(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "accounts"}

    id = Column(String(20), primary_key=True, default=generate_customer_id, unique=True, index=True)
    username = Column(String(20), unique=True, nullable=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    name = Column(String(30), nullable=True)
    phone_no = Column(String(15), unique=True, nullable=True)

    is_active = Column(Boolean, default=True)
    is_email_verified = Column(Boolean, default=False)
    is_phone_no_verified = Column(Boolean, default=False)

    created_dtts = Column(DateTime(timezone=True), default=current_dtts, nullable=False)
    updated_dtts = Column(DateTime(timezone=True), default=current_dtts, onupdate=current_dtts, nullable=False)

    


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    __table_args__ = {"schema": "accounts"}

    token = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("accounts.users.id"), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_dtts = Column(DateTime(timezone=True), default=current_dtts)



class UserOTPModel(Base):
    __tablename__ = "user_otps"
    __table_args__ = {"schema": "accounts"}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(20), ForeignKey("accounts.users.id"), nullable=False)
    
    otp_code = Column(String(6), nullable=False)
    otp_type = Column(String(20), nullable=False)  # email_verification, phone_verification, password_reset
    
    is_used = Column(Boolean, default=False)
    expires_at = Column(DateTime(timezone=True), default=otp_expiry_time, nullable=False)

    created_dtts = Column(DateTime(timezone=True), default=current_dtts, nullable=False)