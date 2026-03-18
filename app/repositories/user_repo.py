from models.user import UserCustomerModel, RefreshToken, UserOTPModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from core.utils import current_dtts
from core.config import settings
from datetime import datetime, timedelta, timezone


class UserCustomerRepository:

    @staticmethod
    async def create(db: AsyncSession, user_data: dict):
        user = UserCustomerModel(**user_data)
        db.add(user)
        await db.flush()
        await db.refresh(user)
        return user

    @staticmethod
    async def get_by_email(db: AsyncSession, email: str):
        stmt = select(UserCustomerModel).where(UserCustomerModel.email == email)
        result = await db.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def get_by_id(db : AsyncSession, id: str):
        stmt = select(UserCustomerModel).where(UserCustomerModel.id == id)
        result = await db.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def get_by_username(db: AsyncSession, username:str):
        stmt = select(UserCustomerModel).where(UserCustomerModel.username == username)
        result = await db.execute(stmt)
        return result.scalars().first()



class RefreshTokenRepository:

    @staticmethod
    async def create(db: AsyncSession, token_data: dict):
        token = RefreshToken(**token_data)
        db.add(token)
        await db.commit()

    @staticmethod
    async def delete_by_token(db: AsyncSession, token: str):
        stmt = delete(RefreshToken).where(RefreshToken.token == token)
        await db.execute(stmt)
        await db.commit()

    @staticmethod
    async def get_by_token(db: AsyncSession, refresh_token: str):
        stmt = select(RefreshToken).where(RefreshToken.token == refresh_token)
        result = await db.execute(stmt)
        return result.scalars().first()


class UserOTPRepository:

    @staticmethod
    async def create_otp(db: AsyncSession, user_otp_data: dict):
        user = UserOTPModel(**user_otp_data)
        db.add(user)
        await db.flush()
        await db.refresh(user)
        return user

    @staticmethod
    async def get_otp_detail(db: AsyncSession, user_id: int, otp_type: str):
        stmt = select(UserOTPModel).where(
                    UserOTPModel.user_id == user_id, 
                    UserOTPModel.otp_type == otp_type
                )
        result = await db.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def change_otp_status(db: AsyncSession, user_id: int, otp_type: str):
        stmt = (
            update(UserOTPModel)
            .where(
                UserOTPModel.user_id == user_id,
                UserOTPModel.otp_type == otp_type,
                UserOTPModel.is_used == False
            )
            .values(is_used=True)
            .execution_options(synchronize_session="fetch")
        )

        await db.execute(stmt)
        await db.commit()
        
        

    @staticmethod
    async def upsert_otp(db: AsyncSession, user_id: int, otp_type: str, new_otp: str):
        result = await db.execute(
            select(UserOTPModel).where(
                UserOTPModel.user_id == user_id,
                UserOTPModel.otp_type == otp_type
            )
        )

        otp_record = result.scalar_one_or_none()
        expiry_time = current_dtts() + timedelta(minutes=settings.EMAIL_VERIFY_EXPIRE_MINUTES)

        if otp_record:
            otp_record.otp_code = new_otp
            otp_record.expires_at = expiry_time
            otp_record.is_used = False
        else:
            otp_record = UserOTPModel(
                user_id=user_id,
                otp_type=otp_type,
                otp_code=new_otp,
                expires_at=expiry_time,
                is_used=False,
            )
            db.add(otp_record)

        await db.flush()
        await db.refresh(otp_record)

        return otp_record