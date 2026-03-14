
from fastapi import APIRouter, Depends, HTTPException, status, Header, Body
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone
from api.deps import get_db, get_cache

from schemas.user_schema import UserCustomerCreateSchema, UserCustomerLoginSchema, UserCustomerLogoutSchema, UserCustomerOTPSchema
from repositories.user_repo import UserCustomerRepository
from services.user_service import UserCustomerService
from core.response import success_response, error_response
from core.exceptions import AppException
from core.utils import *
from core.config import settings
from core.security import get_password_hash, create_access_token, decode_access_token, verify_password, create_refresh_token
from repositories.user_repo import UserCustomerRepository, RefreshTokenRepository, UserOTPRepository
from services.email_service import EmailService
from models.user import UserOTPModel

router = APIRouter()


@router.post("/register")
async def register(payload: UserCustomerCreateSchema, db: AsyncSession = Depends(get_db)):
    response = await UserCustomerService.register_user(db, payload)
    return success_response(response)



@router.post("/login")
async def login(payload: UserCustomerLoginSchema, db: AsyncSession = Depends(get_db)):
    response = await UserCustomerService.login_user(db, payload)
    return success_response(response)


@router.post("/logout")
async def logout(payload : UserCustomerLogoutSchema, authorization: str = Header(None), db: AsyncSession = Depends(get_db), cache=Depends(get_cache)):
    access_token = authorization.replace("Bearer ", "")
    response = await UserCustomerService.logout_user(db, access_token, payload.refresh_token, cache)
    return success_response(response)


@router.post("/refresh-token")
async def refresh_token(payload: dict, db: AsyncSession = Depends(get_db)):
    refresh_token = payload.get("refresh_token")
    response = await UserCustomerService.generate_access_token(db, refresh_token)
    return success_response(response)


@router.post("/verify-email-address")
async def verify_email(payload: UserCustomerOTPSchema, db: AsyncSession = Depends(get_db)):
    user_id = payload.user_id
    otp = payload.otp.strip()
    otp_type = payload.otp_type

    if not otp:
        return error_response(400, "OTP required")
    
    user = await UserCustomerRepository.get_by_id(db, user_id)
    if not user:
        raise AppException(
            error_code=status.HTTP_404_NOT_FOUND,
            error_desc="User not found"
        )
    
    if user.is_email_verified:
        raise AppException(
            error_code=status.HTTP_409_CONFLICT,
            error_desc="Email address already verified"
        )
    
    await UserCustomerService.verify_otp(db, user_id, otp, otp_type)

    user.is_email_verified = True

    # create JWT token
    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    refresh_token = create_refresh_token()

    await RefreshTokenRepository.create(db,
        {
            "token": refresh_token,
            "user_id": user.id,
            "expires_at": current_dtts() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        },
    )

    # ✅ Single commit here
    await db.commit()
    # return only safe fields
    user_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "name": user.name,
    }

    return {
        "user": user_data,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/resend-email-verification")
async def resend_email_verification(payload: UserCustomerOTPSchema, db: AsyncSession = Depends(get_db)):
    user_id = payload.user_id
    email = payload.email
    username = payload.username
    otp_type = payload.otp_type

    user = await UserCustomerRepository.get_by_id(db, user_id)
    if not user:
        raise AppException(
            error_code=status.HTTP_404_NOT_FOUND,
            error_desc="User not found"
        )
    
    if user.is_email_verified:
        raise AppException(
            error_code=status.HTTP_409_CONFLICT,
            error_desc="Email address already verified"
        )

    await UserCustomerService.resend_otp(db, user_id, email, username, otp_type)
    # response = await UserCustomerService.resend_email_verification(db, payload)
    # return success_response(response)

     # ✅ Single commit here
    await db.commit()

    return {
            "status" : status.HTTP_200_OK,
            "message" : "OTP send successfully"
        }






















@router.get("/test-email")
async def test_email():
    # response = await EmailService.send_email(
    #     to_email="anupmirkute1008@gmail.com",
    #     subject="Test Email",
    #     body="This is a test email from FastAPI"
    # )
    print("dsfsfg")
    response = current_dtts()
    print(f"dfsfrgg"+response)
    return success_response(response)