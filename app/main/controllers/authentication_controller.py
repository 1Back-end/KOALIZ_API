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
from app.main.core.mail import send_account_confirmation_email, send_reset_password_email, send_reset_password_option2_email,send_password_reset_succes_email,send_account_created_succes_email
from app.main.core.security import create_access_token, generate_code, get_password_hash, verify_password, is_valid_password, \
    decode_access_token
from app.main.core.config import Config
from app.main.schemas.user import UserProfileResponse
from app.main.utils.helper import check_pass, generate_randon_key

router = APIRouter(prefix="/auths", tags=["auths"])


@router.post("/login/parent", summary="Sign in with email and password", response_model=schemas.ParentAuthentication)
async def login_parent(
    input: schemas.Login,
    db: Session = Depends(get_db),
) -> schemas.ParentAuthentication:
    """
    Sign in with email and password
    """
    user = crud.parent.authenticate(
        db, email=input.email, password=input.password, role_group="parents"
    )
    if not user:
        raise HTTPException(status_code=400, detail=__("auth-login-failed"))

    if user.status in [models.UserStatusType.BLOCKED, models.UserStatusType.DELETED]:
        raise HTTPException(status_code=400, detail=__("auth-login-failed"))

    if not crud.parent.is_active(user):
        raise HTTPException(status_code=402, detail=__("user-not-activated"))

    # access_token_expires = timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)

    return {
        "user": user,
        "token": {
            "access_token": create_access_token(
                user.uuid
            ),
            "token_type": "bearer",
        }
    }


@router.post("/login/administrator", summary="Sign in with email and password", response_model=schemas.AdministratorAuthentication)
async def login_administrator(
        input: schemas.Login,
        db: Session = Depends(get_db),
) -> schemas.AdministratorAuthentication:
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

    # access_token_expires = timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)

    return {
        "user": user,
        "token": {
            "access_token": create_access_token(
                user.uuid
            ),
            "token_type": "bearer",
        }
    }


@router.post("/login/owner", summary="Sign in with email and password", response_model=schemas.OwnerAuthentication)
async def login_owner(
        input: schemas.Login,
        db: Session = Depends(get_db),
) -> schemas.OwnerAuthentication:
    """
    Sign in with email and password
    """
    user = crud.owner.authenticate(
        db, email=input.email, password=input.password, role_group="owners"
    )
    if not user:
        raise HTTPException(status_code=400, detail=__("auth-login-failed"))

    if user.status in [models.UserStatusType.BLOCKED, models.UserStatusType.DELETED]:
        raise HTTPException(status_code=400, detail=__("auth-login-failed"))

    if not crud.owner.is_active(user):
        raise HTTPException(status_code=402, detail=__("user-not-activated"))

    # access_token_expires = timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)

    return {
        "user": user,
        "token": {
            "access_token": create_access_token(
                user.uuid
            ),
            "token_type": "bearer",
        }
    }


@router.get("/me", summary="Get current user", response_model=UserProfileResponse)
def get_current_user(
        current_user: any = Depends(TokenRequired()),
) -> schemas.UserProfileResponse:
    """
    Get current user
    """

    return current_user


@router.post("/adminstrator/start-reset-password", summary="Start reset password with phone number", response_model=schemas.Msg)
def start_reset_password(
        input: schemas.ResetPasswordOption2Step1,
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

    token = create_access_token(
                user.uuid, expires_delta=timedelta(minutes=30)
            )

    user_code = models.AdminActionValidation(
        uuid=str(uuid.uuid4()),
        code=token,
        user_uuid=user.uuid,
        expired_date=datetime.now() + timedelta(minutes=30)
    )
    db.add(user_code)
    db.commit()

    send_reset_password_option2_email(
        email_to=user.email, name=user.firstname, token=token, valid_minutes=30, language=input.language
    )

    return schemas.Msg(message=__("reset-password-started"))


@router.put("/adminstrator/reset-password", summary="Reset password", response_model=schemas.Msg)
def reset_password(
        input: schemas.ResetPasswordOption2Step2,
        db: Session = Depends(get_db),
) -> schemas.Msg:
    """
    Reset password
    """
    token_data = decode_access_token(input.token)
    if not token_data:
        raise HTTPException(status_code=403, detail=__("token-invalid"))

    user = crud.administrator.get_by_uuid(db, token_data["sub"])

    user_code: models.AdminActionValidation = db.query(models.AdminActionValidation).filter(
        models.AdminActionValidation.code == input.token).filter(
        models.AdminActionValidation.user_uuid == user.uuid).filter(
        models.AdminActionValidation.expired_date >= datetime.now()).first()
    if not user_code:
        raise HTTPException(status_code=403, detail=__("token-invalid"))

    elif not crud.administrator.is_active(user):
        raise HTTPException(status_code=400, detail=__("user-not-activated"))

    if not is_valid_password(password=input.new_password):
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
    
    if not is_valid_password(password=input.otp):
        raise HTTPException(
            status_code=400,
            detail=__("password-invalid")
        )
    send_password_reset_succes_email(user.email,(user.firstname +" "+ user.lastname),user_code.value)

    db.delete(user_code)

    user.password_hash = get_password_hash(input.new_password)
    db.add(user)
    db.commit()

    return schemas.Msg(message=__("password-reset-successfully"))


@router.post("/owner/start-reset-password", summary="Start reset password with phone number", response_model=schemas.Msg)
def start_reset_password(
        input: schemas.ResetPasswordOption2Step1,
        db: Session = Depends(get_db),
) -> schemas.Msg:
    """
    Start reset password
    """
    user = crud.owner.get_by_email(db=db, email=input.email)
    if not user:
        raise HTTPException(status_code=404, detail=__("user-not-found"))

    elif not crud.owner.is_active(user):
        raise HTTPException(status_code=400, detail=__("user-not-activated"))

    token = create_access_token(
                user.uuid, expires_delta=timedelta(minutes=30)
            )

    user_code = models.OwnerActionValidation(
        uuid=str(uuid.uuid4()),
        code=token,
        user_uuid=user.uuid,
        expired_date=datetime.now() + timedelta(minutes=30)
    )
    db.add(user_code)
    db.commit()

    send_reset_password_option2_email(
        email_to=user.email, name=user.firstname, token=token, valid_minutes=30, language=input.language
    )

    return schemas.Msg(message=__("reset-password-started"))


@router.put("/owner/reset-password", summary="Reset password", response_model=schemas.Msg)
def reset_password(
        input: schemas.ResetPasswordOption2Step2,
        db: Session = Depends(get_db),
) -> schemas.Msg:
    """
    Reset password
    """
    token_data = decode_access_token(input.token)
    if not token_data:
        raise HTTPException(status_code=403, detail=__("token-invalid"))

    user = crud.owner.get_by_uuid(db, token_data["sub"])

    user_code: models.OwnerActionValidation = db.query(models.OwnerActionValidation).filter(
        models.OwnerActionValidation.code == input.token).filter(
        models.OwnerActionValidation.user_uuid == user.uuid).filter(
        models.OwnerActionValidation.expired_date >= datetime.now()).first()
    if not user_code:
        raise HTTPException(status_code=403, detail=__("token-invalid"))

    elif not crud.owner.is_active(user):
        raise HTTPException(status_code=400, detail=__("user-not-activated"))

    if not is_valid_password(password=input.new_password):
        raise HTTPException(
            status_code=400,
            detail=__("password-invalid")
        )
    send_password_reset_succes_email(user.email,(user.firstname +" "+ user.lastname),user_code.value)

    db.delete(user_code)

    user.password_hash = get_password_hash(input.new_password)
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
    
    send_password_reset_succes_email(current_user.email,(current_user.firstname +" "+ current_user.lastname),new_password)

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

    # access_token_expires = timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)

    return {
        "user": user,
        "token": {
            "access_token": create_access_token(
                user.uuid
            ),
            "token_type": "bearer",
        }
    }

@router.post("/parent", response_model=schemas.Msg)
async def create_parent_on_system(
    input: schemas.ParentCreate,
    db: Session = Depends(get_db),
) -> Any:
    """
    Create the parent in the system
    """
    user = crud.parent.get_by_email(db,input.email)
    if input.avatar_uuid:
        avatar = crud.storage.get(db,input.avatar_uuid)
        if not avatar:
            raise HTTPException(status_code=404, detail=__("avatar-not-found"))

    code = generate_code(length=12)
    code= str(code[0:6]) 
    
    if not is_valid_password(password=input.password):
        raise HTTPException(
            status_code=400,
            detail=__("password-invalid")
        )
    
    if user:
        if crud.parent.is_active(user):
            raise HTTPException(status_code=400, detail=__("user-email-taken"))

        user_code: models.ParentActionValidation = db.query(models.ParentActionValidation).filter(
        models.ParentActionValidation.user_uuid == user.uuid)

        if user_code.count()>0:
            user_code.delete()

        print("user_code1:")
        db_code = models.ParentActionValidation(
            uuid=str(uuid.uuid4()),
            code=code,
            user_uuid=user.uuid,
            value=code,
            expired_date=datetime.now() + timedelta(minutes=30)
        )

        db.add(db_code)
        db.commit()
        send_account_confirmation_email(email_to=input.email, name=(input.firstname+input.lastname),token=code,valid_minutes=30)

    else:
        crud.parent.create(db=db, obj_in=input,code=code)

    return schemas.Msg(message=__("account-validation-pending"))

@router.post("/parent/validate-account", response_model=schemas.ParentAuthentication)
def validate_account(
        input: schemas.ValidateAccount,
        db: Session = Depends(get_db),
) -> schemas.Msg:
    """
    validate Account
    """

    user = crud.parent.get_by_email(db, email=input.email)
    if not user:
        raise HTTPException(status_code=404, detail=__("user-not-found"))
    
    user_code: models.ParentActionValidation = db.query(models.ParentActionValidation).filter(
        models.ParentActionValidation.code == input.token).filter(
        models.ParentActionValidation.user_uuid == user.uuid).filter(
        models.ParentActionValidation.expired_date >= datetime.now()).first()
    
    if not user_code:
        raise HTTPException(status_code=403, detail=__("invalid-user"))
    
    db.delete(user_code)
    db.commit()

    user.status = models.UserStatusType.ACTIVED
    # user.otp = None
    # user.otp_expired_at = None
    send_account_created_succes_email(user.email,(user.firstname + " " +user.lastname))
    db.commit()
    db.refresh(user)

    # access_token_expires = timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)

    return {
        "user": user,
        "token": {
            "access_token": create_access_token(
                user.uuid
            ),
            "token_type": "bearer",
        }
    }


@router.post("/parent/password-validation", response_model=schemas.Msg)
def validate_password(
        input: schemas.ValidateAccount,
        db: Session = Depends(get_db),
) -> schemas.Msg:
    """
    validate password
    """

    user = crud.parent.get_by_email(db, email=input.email)
    if not user:
        raise HTTPException(status_code=404, detail=__("user-not-found"))

    user_code: models.ParentActionValidation = db.query(models.ParentActionValidation).filter(
        models.ParentActionValidation.code == input.token).filter(
        models.ParentActionValidation.user_uuid == user.uuid).filter(
        models.ParentActionValidation.expired_date >= datetime.now()).first()
    
    if not user_code:
        raise HTTPException(status_code=403, detail=__("invalid-user"))

    return {"message":__("Ok")}


    

@router.post("/parent/start-reset-password", summary="Start reset password with email", response_model=schemas.Msg)
def start_reset_password(
        input: schemas.ResetPasswordOption2Step1,
        db: Session = Depends(get_db),
) -> schemas.Msg:
    """
    Start reset password
    """
    user = crud.parent.get_by_email(db=db, email=input.email)
    if not user:
        raise HTTPException(status_code=404, detail=__("user-not-found"))

    elif not crud.parent.is_active(user):
        raise HTTPException(status_code=400, detail=__("user-not-activated"))

    
    # Generate code for validation after
    code = generate_code(length=12)
    code = str(code[0:6])
    user_code = models.ParentActionValidation(
        uuid=str(uuid.uuid4()),
        code=code[:6],
        user_uuid=user.uuid,
        expired_date=datetime.now() + timedelta(minutes=30)
    )
    db.add(user_code)
    db.commit()

    send_reset_password_email(
        email_to=user.email, name=(user.firstname or "")+" "+(user.lastname or ""), token=code, valid_minutes=30
    )

    return schemas.Msg(message=__("reset-password-started"))

@router.post("/parent/code/send", summary="send code", response_model=schemas.Msg)
def send_code(
        input: schemas.ResetPasswordOption2Step1,
        db: Session = Depends(get_db),
) -> schemas.Msg:
    """
    Start reset password
    """
    user = crud.parent.get_by_email(db=db, email=input.email)
    if not user:
        raise HTTPException(status_code=404, detail=__("user-not-found"))

    # Generate code for validation after
    code = generate_code(length=12)
    code = str(code[0:6])

    user_code: models.ParentActionValidation = db.query(models.ParentActionValidation).filter(
        models.ParentActionValidation.user_uuid == user.uuid)

    if user_code.count()>0:
        user_code.delete()
        db.flush()

    db_code = models.ParentActionValidation(
        uuid=str(uuid.uuid4()),
        code=code,
        user_uuid=user.uuid,
        value=code,
        expired_date=datetime.now() + timedelta(minutes=30)
    )

    db.add(db_code)
    db.commit()

    send_account_confirmation_email(email_to=input.email, name=(user.firstname+user.lastname),token=code,valid_minutes=30)

    return schemas.Msg(message=__("account-validation-pending"))


@router.put("/parent/reset-password", summary="Reset password", response_model=schemas.Msg)
def reset_password(
        input: schemas.ResetPasswordOption2Step2,
        db: Session = Depends(get_db),
) -> schemas.Msg:
    """
    Reset password
    """

    token_data = db.query(models.ParentActionValidation).filter(
        models.ParentActionValidation.code == input.token).filter(
        models.ParentActionValidation.expired_date >= datetime.now()).first()
    if not token_data:
        raise HTTPException(status_code=403, detail=__("token-invalid"))

    user = crud.parent.get_by_uuid(db, token_data.user_uuid)

    user_code = db.query(models.ParentActionValidation).filter(
        models.ParentActionValidation.code == input.token).filter(
        models.ParentActionValidation.user_uuid == token_data.user_uuid).filter(
        models.ParentActionValidation.expired_date >= datetime.now()).first()
    if not user_code:
        raise HTTPException(status_code=403, detail=__("token-invalid"))

    elif not crud.parent.is_active(user):
        raise HTTPException(status_code=400, detail=__("user-not-activated"))

    if not is_valid_password(password=input.new_password):
        raise HTTPException(
            status_code=400,
            detail=__("password-invalid")
        )

    db.delete(user_code)
    send_password_reset_succes_email(user.email,(user.firstname +" "+ user.lastname),input.new_password)

    user.password_hash = get_password_hash(input.new_password)
    db.add(user)
    db.commit()

    return schemas.Msg(message=__("password-reset-successfully"))

@router.put("/parent/restore-password", summary="restore password when not logged in", response_model=schemas.Msg)
def restore_password(
        input: schemas.ResetPasswordOption2Step2,
        db: Session = Depends(get_db),
) -> schemas.Msg:
    """
    Reset password
    """

    token_data = db.query(models.ParentActionValidation).filter(
        models.ParentActionValidation.code == input.token).filter(
        models.ParentActionValidation.expired_date >= datetime.now()).first()
    if not token_data:
        raise HTTPException(status_code=403, detail=__("token-invalid"))

    user = crud.parent.get_by_uuid(db, token_data.user_uuid)

    user_code = db.query(models.ParentActionValidation).filter(
        models.ParentActionValidation.code == input.token).filter(
        models.ParentActionValidation.user_uuid == token_data.user_uuid).filter(
        models.ParentActionValidation.expired_date >= datetime.now()).first()
    if not user_code:
        raise HTTPException(status_code=403, detail=__("token-invalid"))
    
    if not is_valid_password(password=input.new_password):
        raise HTTPException(
            status_code=400,
            detail=__("password-invalid")
        )

    send_password_reset_succes_email(user.email,(user.firstname +" "+ user.lastname),input.new_password)

    db.delete(user_code)

    user.password_hash = get_password_hash(input.new_password)
    db.add(user)
    db.commit()

    return schemas.Msg(message=__("password-reset-successfully"))
