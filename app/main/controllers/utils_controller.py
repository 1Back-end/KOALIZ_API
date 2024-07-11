from typing import Union

from fastapi import APIRouter, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.main import schemas, models, crud
from app.main.core.dependencies import get_db, TokenRequired
from app.main.core.i18n import __
from app.main.core.security import decode_access_token, is_apikey
from app.main.crud import user
from app.main.models import BlacklistToken
from app.main.models.db.session import SessionLocal

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get("/validate-token/{token}", status_code=200)
async def validate_token(
        token: str,
):
    """Validate token"""
    db = SessionLocal()
    print(f".............token: {token}")
    if BlacklistToken.check_blacklist(db=db, auth_token=token):
        db.close()
        return False
    db.close()
    token = decode_access_token(token)
    print(f".............token: {token}")
    return token


@router.get("/get_user/{token}/{user_uuid}", status_code=200)
async def validate_token(
        token: str,
        user_uuid: str,
):
    """Validate token"""
    db = SessionLocal()
    if BlacklistToken.check_blacklist(db=db, auth_token=token):
        db.close()
        return False
    db.close()
    current_user = user.get_by_uuid(db=db, uuid=user_uuid)
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")
    return current_user


@router.get("/get_users/{token}/{uuid}", status_code=200)
async def get_users(
        token: str,
        uuid: str,
):
    """Get users"""
    db = SessionLocal()
    if BlacklistToken.check_blacklist(db=db, auth_token=token):
        db.close()
        return False
    db.close()
    print(f"...........uuid come from front:{uuid}")
    print(".............new format_buyer:{}, seller:{}".format(decode_access_token(token)['sub'], uuid))
    users = []
    user1 = user.get_by_uuid(db=db, uuid=decode_access_token(token)['sub'])
    user2 = user.get_by_uuid(db=db, uuid=uuid)
    if not user1:
        raise HTTPException(status_code=404, detail="User not found")
    users.append(user1)
    if not user2:
        raise HTTPException(status_code=404, detail="User not found")
    users.append(user2)
    print(".............buyer:{}, seller:{}".format(user1, user2))
    return users


@router.post("/device/{player_id}", response_model=schemas.Msg)
def add_device(
        player_id: str,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(TokenRequired())
) -> schemas.Msg:
    """
        Create device id for Onesignal.
    """

    devices = db.query(models.Device).filter_by(player_id=player_id).all()
    if devices:
        for device in devices:
            db.delete(device)
            db.commit()

    device = models.Device(
        user_uuid=current_user.uuid,
        player_id=player_id
    )
    db.add(device)
    db.commit()

    return schemas.Msg(message=__("device-add-success"))


@router.delete("/device/{player_id}", response_model=schemas.Msg)
def remove_device(
        *,
        db: Session = Depends(get_db),
        player_id: str,
        current_user: models.User = Depends(TokenRequired())
) -> schemas.Msg:
    """
        Delete device id for Onesignal.
    """

    devices = db.query(models.Device).filter_by(player_id=player_id).all()
    for device in devices:
        db.delete(device)
        db.commit()

    return schemas.Msg(message=__("device-deleted-success"))


@router.get("/devices/{user_uuid}", response_model=Union[list[str], bool])
def get_device_by_user_uuid(api_key: str, user_uuid: str) -> Union[list[str], bool]:
    """
        Get a user devices for Onesignal.
    """
    try:
        is_apikey(api_key=api_key)
        db = SessionLocal()

        return [device.player_id
                for device in
                db.query(models.Device).filter(models.Device.user_uuid == user_uuid).all()]
    except Exception as e:
        print(f"======={e}")
        return False


@router.post("/user/one/{token}/{user_uuid}", summary="Get current user", response_model=schemas.UserProfileResponse)
def get_user_one(
        token:str,
        user_uuid:str,
        api_key:str,
        db: Session = Depends(get_db)
):

    exist_storage = None
    decode_access_token(token)

    is_apikey(api_key=api_key)
    if not api_key:
        raise HTTPException(status_code=403, detail=__("bad-api-key"))

    if not decode_access_token(token):
        raise HTTPException(status_code=403, detail=__("invalid-token"))

    if BlacklistToken.check_blacklist(db=db, auth_token=token):
       raise HTTPException(status_code=401, detail=__("unauthorized"))

    if not decode_access_token(token)['sub'] == user_uuid:
        raise HTTPException(status_code=401, detail=__("unauthorized"))

    user = crud.user.get_by_uuid(db=db, uuid=decode_access_token(token)['sub'])

    if user.storage_uuid is not None:
        storage_uuids = [user.storage_uuid]
        exist_storage = exist_storage[0]
        user = jsonable_encoder(user)
        user["avatar"] = exist_storage
    return user
