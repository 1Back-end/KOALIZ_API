import uuid
from datetime import timedelta, datetime
from typing import Any, Optional, List
from fastapi import APIRouter, Depends, Body, HTTPException, Query, File
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from starlette.requests import Request

from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from app.main.core.security import create_access_token, get_password_hash, decode_access_token
from app.main.core.config import Config
from app.main.schemas.user import UserProfileResponse

router = APIRouter(prefix="/auths", tags=["auths"])


@router.post("/login/administrator", summary="Sign in with email and password", response_model=schemas.UserAuthentication)
async def login(
        input: schemas.Login,
        db: Session = Depends(get_db),
) -> schemas.UserAuthentication:
    """
    Sign in with email and password
    """
    user = crud.user.authenticate(
        db, email=input.email, password=input.password
    )
    if not user:
        raise HTTPException(status_code=400, detail=__("auth-login-failed"))

    if user.status in [models.UserStatusType.BLOCKED, models.UserStatusType.DELETED]:
        raise HTTPException(status_code=400, detail=__("auth-login-failed"))

    if user.status != models.UserStatusType.ACTIVED:
        raise HTTPException(status_code=402, detail=__("user-not-activated"))

    access_token_expires = timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)

    return {
        "user": user,
        "token": {
            "access_token": create_access_token(
                user.uuid, expires_delta=access_token_expires
            ),
            "token_type": "bearer",
        }
    }


@router.post("/validate-account", summary="Verify OTP", response_model=schemas.UserAuthentication, include_in_schema=False)
async def verify_otp(
        phone_number: str = Body(...),
        otp: str = Body(...),
        country_code: str = Body(...),
        db: Session = Depends(get_db),
) -> Any:
    """
    Validate account with OTP
    """
    user = crud.user.get_by_phone_number(db=db, phone_number=f"{country_code}{phone_number}")
    print(f"...........phone number: {user}")
    if not user:
        raise HTTPException(status_code=404, detail=__("user-not-found"))

    if user.otp != otp:
        raise HTTPException(status_code=400, detail=__("otp-invalid"))

    if user.otp_expired_at < datetime.now():
        raise HTTPException(status_code=400, detail=__("otp-expired"))

    user.status = models.UserStatusType.ACTIVED
    user.otp = None
    user.otp_expired_at = None

    db.commit()
    db.refresh(user)

    access_token_expires = timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)

    return {
        "user": user,
        "token": {
            "access_token": create_access_token(
                user.uuid, expires_delta=access_token_expires
            ),
            "token_type": "bearer",
        }
    }


@router.post("/start-reset-password", summary="Start reset password with phone number", response_model=schemas.Msg, include_in_schema=False)
def start_reset_password(
        phone_number: str = Body(...),
        country_code: str = Body(...),
        db: Session = Depends(get_db),

) -> schemas.Msg:
    """
    Start reset password with phone number
    """
    user = crud.user.get_by_phone_number(db=db, phone_number=f"{country_code}{phone_number}")
    if not user:
        raise HTTPException(status_code=404, detail=__("user-not-found"))

    user.otp_password = "00000"
    user.otp_password_expired_at = datetime.now() + timedelta(minutes=5)
    db.commit()
    db.refresh(user)

    return schemas.Msg(message=__("reset-password-started"))


@router.post("/check-otp-password", summary="Check OTP password", response_model=schemas.Msg, include_in_schema=False)
def check_otp_password(
        phone_number: str = Body(...),
        otp: str = Body(...),
        country_code: str = Body(...),
        db: Session = Depends(get_db),
) -> schemas.Msg:
    """
    Check OTP password
    """
    user = crud.user.get_by_phone_number(db=db, phone_number=f"{country_code}{phone_number}")
    if not user:
        raise HTTPException(status_code=404, detail=__("user-not-found"))

    if user.otp_password != otp:
        raise HTTPException(status_code=400, detail=__("otp-invalid"))

    if user.otp_password_expired_at < datetime.now():
        raise HTTPException(status_code=400, detail=__("otp-expired"))

    return schemas.Msg(message=__("otp-valid"))


@router.post("/reset-password", summary="Reset password", response_model=schemas.Msg, include_in_schema=False)
def reset_password(
        phone_number: str = Body(...),
        otp: str = Body(...),
        password: str = Body(...),
        country_code: str = Body(...),
        db: Session = Depends(get_db),
) -> schemas.Msg:
    """
    Reset password
    """
    user = crud.user.get_by_phone_number(db=db, phone_number=f"{country_code}{phone_number}")
    if not user:
        raise HTTPException(status_code=404, detail=__("user-not-found"))

    if user.otp_password != otp:
        raise HTTPException(status_code=400, detail=__("otp-invalid"))

    if user.otp_password_expired_at < datetime.now():
        raise HTTPException(status_code=400, detail=__("otp-expired"))

    user.password_hash = get_password_hash(password=password)
    user.otp_password = None
    user.otp_password_expired_at = None
    db.commit()
    db.refresh(user)

    return schemas.Msg(message=__("password-reset-successfully"))


@router.get("/me", summary="Get current user", response_model=UserProfileResponse)
def get_current_user(
        current_user: models.User = Depends(TokenRequired()),
        db: Session = Depends(get_db),
) -> schemas.UserProfileResponse:
    """
    Get current user
    """

    return current_user


@router.put("/users/profile", response_model=UserProfileResponse, include_in_schema=False)
async def update_user_profile(
        obj_in: schemas.UserUpdate,
        db: Session = Depends(get_db)
):
    if not crud.user.get_by_uuid(db=db, uuid=obj_in.user_uuid):
        raise HTTPException(status_code=404, detail="User not found")

    return crud.user.update_profile(obj_in=obj_in, db=db)
