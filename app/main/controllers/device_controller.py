from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.main.core.security import create_access_token, generate_code


router = APIRouter(prefix="/devices", tags=["devices"])


@router.post("", response_model=schemas.Device, status_code=200)
def get_details(
    name: str,
    db: Session = Depends(get_db),
):
    """
        Get device details
    """
    device = crud.device.get_by_device_name(db, name)
    if not device:
        token = create_access_token(name)

        # Generate code for validation after
        code = generate_code(length=6)
        qrcode = crud.storage.store_qrcode(db=db, code=code)

        obj= schemas.DeviceCreate(
            name=name,
            token=token,
            code=code,
            qrcode_uuid=qrcode.uuid if qrcode else None
        )
        device = crud.device.create(db=db, obj_in=obj)

    return device

@router.post("/verification", response_model=schemas.DeviceAuthentication, status_code=200)
def device_verification(
    code: str,
    db: Session = Depends(get_db),
):
    """
        Get device details
    """
    device = crud.device.get_by_device_code(db, code)
    if not device:
        raise HTTPException(status_code=404, detail=__("device-not-found"))

    return {
        "device": device,
        "token": {
            "access_token": device.token,
            "token_type": "bearer",
        }
    }