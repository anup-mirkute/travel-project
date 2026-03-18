from datetime import datetime, timedelta, timezone
from core.utils import current_dtts

from repositories.user_repo import UserCustomerRepository, RefreshTokenRepository, UserOTPRepository
from core.security import get_password_hash, create_access_token, decode_access_token, verify_password, create_refresh_token
from core.exceptions import AppException
from core.config import settings
from core.utils import generate_otp

from services.email_service import EmailService
from fastapi import status


class UserCustomerService:

    @staticmethod
    async def register_user(db, payload):
        async with db.begin():

            if await UserCustomerRepository.get_by_email(db, payload.email):
                raise AppException(
                    error_code=status.HTTP_400_BAD_REQUEST,
                    error_desc="Email already registered"
                )

            if payload.username and await UserCustomerRepository.get_by_username(db, payload.username):
                raise AppException(
                    error_code=status.HTTP_400_BAD_REQUEST,
                    error_desc="Username already exists"
                )

            data = payload.model_dump()
            data["password"] = get_password_hash(data["password"])

            user = await UserCustomerRepository.create(db, data)

            otp = generate_otp()
            expiry_time = current_dtts() + timedelta(minutes=settings.EMAIL_VERIFY_EXPIRE_MINUTES)
            user_otp_data = {
                'user_id' : user.id, 
                'otp_code' : otp, 
                'otp_type' : settings.OTP_TYPE[0],
                'expires_at' : expiry_time,
            }

            otp_record = await UserOTPRepository.create_otp(db, user_otp_data)

        # Send email AFTER transaction
        # await EmailService.send_email(
        #     to_email=user.email,
        #     subject="Verify your email",
        #     body=f"Hello {user.username}, your OTP is: {otp}."
        # )

        return {
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "name": user.name,
            }
        }

    @staticmethod
    async def login_user(db, payload):
        user = await UserCustomerRepository.get_by_email(db, payload.email)

        if not user:
            raise AppException(
                error_code=status.HTTP_401_UNAUTHORIZED,
                error_desc="Incorrect Credentials"
            )
        
        if not verify_password(payload.password, user.password):
            raise AppException(
                error_code=status.HTTP_401_UNAUTHORIZED,
                error_desc="Incorrect Credentials"
            )

        access_token = create_access_token({"sub": user.id}, expires_delta=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token = create_refresh_token()

        await RefreshTokenRepository.create(db, {
            "token": refresh_token,
            "user_id": user.id,
            "expires_at": current_dtts() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        })

        return {
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "name": user.name,
            },
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    @staticmethod
    async def logout_user(db, access_token: str, refresh_token: str, cache):

        # if access_token:
        #     await cache.delete(access_token)
        
        if refresh_token:
            await RefreshTokenRepository.delete_by_token(db, refresh_token)

        return {
            "status" : status.HTTP_200_OK,
            "message" : "Logged out successfully"
        }

    @staticmethod
    async def generate_access_token(db, refresh_token : str):
        token_data = await RefreshTokenRepository.get_by_token(db, refresh_token)

        if not token_data:
            raise AppException(
                error_code=status.HTTP_401_UNAUTHORIZED,
                error_desc="Invalid refresh token"
            )

        if token_data.expires_at < current_dtts():
            raise AppException(
                error_code=status.HTTP_401_UNAUTHORIZED,
                error_desc="Refresh token expired"
            )

        new_access_token = create_access_token(data={"sub": token_data.user_id})

        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }

    @staticmethod
    async def verify_otp(db, user_id: str, otp: str, otp_type: str):
        stored_otp = await UserOTPRepository.get_otp_detail(db, user_id, otp_type)

        if not stored_otp:
            raise AppException(
                error_code=status.HTTP_400_BAD_REQUEST,
                error_desc="No OTP found, please request a new one"
            )

        if stored_otp.is_used:
            raise AppException(
                error_code=status.HTTP_400_BAD_REQUEST,
                error_desc="OTP already used"
            )

        if stored_otp.expires_at < current_dtts():
            raise AppException(
                error_code=status.HTTP_400_BAD_REQUEST,
                error_desc="OTP expired"
            )
        
        if stored_otp.otp_code != otp:
            raise AppException(
                error_code=status.HTTP_400_BAD_REQUEST,
                error_desc="Invalid OTP"
            )
        
        await UserOTPRepository.change_otp_status(db, user_id, otp_type)

        return True
        
            
    @staticmethod
    async def resend_otp(db, user_id: str, email: str, username: str, otp_type: str):
        stored_otp = await UserOTPRepository.get_otp_detail(db, user_id, otp_type)

        if not stored_otp:
            raise AppException(
                error_code=status.HTTP_400_BAD_REQUEST,
                error_desc="Something went wrong."
            )

        otp = generate_otp()
        otp_record = await UserOTPRepository.upsert_otp(db, user_id, otp_type, otp)

        # Send email AFTER transaction
        # await EmailService.send_email(
        #     to_email=email,
        #     subject="Your new OTP",
        #     body=f"Hello {username}, your new OTP is: {otp}."
        # )
        return True