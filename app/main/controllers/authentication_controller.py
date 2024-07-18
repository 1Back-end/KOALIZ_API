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
from app.main.core.mail import send_reset_password_email
from app.main.core.security import create_access_token, get_password_hash, verify_password, is_valid_password
from app.main.core.config import Config
from app.main.schemas.user import UserProfileResponse
from app.main.utils.helper import check_pass, generate_randon_key

router = APIRouter(prefix="/auths", tags=["auths"])


@router.post("/login/administrator", summary="Sign in with email and password", response_model=schemas.AdministratorAuthentication)
async def login(
        input: schemas.Login,
        db: Session = Depends(get_db),
) -> schemas.UserAuthentication:
    """
    Sign in with email and password
    """
    user = crud.administrator.authenticate(
        db, email=input.email, password=input.password, role_group="administrators"
    )
    if not user:
        raise HTTPException(status_code=400, detail=__("auth-login-failed"))

    if user.status in [models.UserStatusType.BLOCKED, models.UserStatusType.DELETED]:
        raise HTTPException(status_code=400, detail=__("auth-login-failed"))

    if not crud.administrator.is_active(user):
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


@router.get("/me", summary="Get current user", response_model=UserProfileResponse)
def get_current_user(
        current_user: models.User = Depends(TokenRequired()),
) -> schemas.UserProfileResponse:
    """
    Get current user
    """

    return current_user


@router.post("/adminstrator/start-reset-password", summary="Start reset password with phone number", response_model=schemas.Msg)
def start_reset_password(
        input: schemas.ResetPasswordStep1,
        db: Session = Depends(get_db),
) -> schemas.Msg:
    """
    Start reset password
    """
    user = crud.administrator.get_by_email(db=db, email=input.email)
    if not user:
        raise HTTPException(status_code=404, detail=__("user-not-found"))

    elif not crud.administrator.is_active(user):
        raise HTTPException(status_code=400, detail=__("user-not-activated"))

    is_valid_password = check_pass(password=input.new_password)
    if not is_valid_password:
        raise HTTPException(
            status_code=400,
            detail=__("password-invalid")
        )

    code = generate_randon_key(length=5)

    # user.otp_password = "00000"
    # user.otp_password_expired_at = datetime.now() + timedelta(minutes=5)

    user_code = models.AdminActionValidation(
        uuid=str(uuid.uuid4()),
        code=str(code),
        user_uuid=user.uuid,
        value=get_password_hash(input.new_password),
        expired_date=datetime.now() + timedelta(minutes=5)
    )
    db.add(user_code)
    db.commit()

    send_reset_password_email(
        email_to=user.email, name=user.firstname, token=code, valid_minutes=5
    )

    return schemas.Msg(message=__("reset-password-started"))


@router.put("/administrator/reset-password", summary="Reset password", response_model=schemas.Msg)
def reset_password(
        input: schemas.ResetPasswordStep2,
        db: Session = Depends(get_db),
) -> schemas.Msg:
    """
    Reset password
    """
    user = crud.administrator.get_by_email(db, email=input.email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail=__("user-email-not-found")
        )
    elif not crud.administrator.is_active(user):
        raise HTTPException(status_code=400, detail=__("user-not-activated"))

    user_code: models.AdminActionValidation = db.query(models.AdminActionValidation).filter(models.AdminActionValidation.code==input.otp).filter(
        models.AdminActionValidation.user_uuid == user.uuid).filter(
        models.AdminActionValidation.expired_date >= datetime.now()).first()
    if not user_code:
        raise HTTPException(
            status_code=404,
            detail=__("validation-code-not-found"),
        )

    db.delete(user_code)

    user.password_hash = user_code.value
    db.add(user)
    db.commit()

    return schemas.Msg(message=__("password-reset-successfully"))


@router.put("/me/password", response_model=schemas.UserProfileResponse)
async def update_current_user_password(
        new_password: str,
        current_password: str,
        db: Session = Depends(get_db),
        # current_user: any = Depends(TokenRequired())
        current_user: any = Depends(TokenRequired(let_new_user=True))
) -> schemas.UserProfileResponse:
    """
        Update password of current connected user
    """
    if not verify_password(plain_password=current_password, hashed_password=current_user.password_hash):
        raise HTTPException(status_code=400, detail=__("incorrect-current-password"))

    # Check if new password is equal to current
    if verify_password(plain_password=new_password, hashed_password=current_user.password_hash):
        raise HTTPException(status_code=400, detail=__("different-password-required"))

    if not is_valid_password(password=new_password):
        raise HTTPException(status_code=400, detail=__("invalid-password"))

    current_user.password_hash = get_password_hash(new_password)
    if current_user.is_new_user:
        current_user.is_new_user = False
    db.commit()

    return current_user

@router.put("/users/profile", response_model=UserProfileResponse, include_in_schema=False)
async def update_user_profile(
        obj_in: schemas.UserUpdate,
        db: Session = Depends(get_db)
):
    if not crud.user.get_by_uuid(db=db, uuid=obj_in.user_uuid):
        raise HTTPException(status_code=404, detail="User not found")

    return crud.user.update_profile(obj_in=obj_in, db=db)



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
