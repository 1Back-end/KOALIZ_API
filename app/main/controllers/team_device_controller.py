import uuid
from app.main.core import dependencies
from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Any, Optional

from app.main.core.security import create_access_token, generate_code


router = APIRouter(prefix="/devices", tags=["devices"])


@router.post("/login", response_model=schemas.TeamDeviceAuthentication, status_code=200)
def team_device_login(
    code: str,
    db: Session = Depends(get_db),
):
    """
        Team device login
    """
    return "BBBBBBBBBBBBBBBBBBBBBBBBB"
    team_device = crud.team_device.get_by_team_device_code(db, code)
    if not team_device:
        raise HTTPException(status_code=404, detail=__("device-not-found"))

    token = create_access_token(team_device.uuid)
    team_device.token = token
    db.commit()

    return {
        "token": {
            "access_token": token,
            "token_type": "bearer",
        },
        "team_device": team_device
    }

@router.get("/me", response_model=schemas.TeamDeviceSlim)
def current_team_device(
        current_team_device: models.TeamDevice = Depends(dependencies.TeamTokenRequired(roles=[])),
) -> schemas.TeamDevice:
    """
    Get current team device
    """

    return current_team_device

@router.delete("/logout", status_code=200)
def logout(
    *,
    db: Session = Depends(dependencies.get_db),
    current_team_device: any = Depends(dependencies.TeamTokenRequired(roles=[])),
    token: str = Query(...),
) -> Any:
    """
        Logout team device and blacklist token
    """

    db.add(models.BlacklistToken(token=token, uuid=str(uuid.uuid4())))
    team_device = db.query(models.TeamDevice).filter(models.TeamDevice.token==token).first()
    if team_device:
        team_device.token = None
    db.commit()
    raise HTTPException(status_code=200, detail=None)


@router.get("/details", response_model=schemas.TeamDevice, status_code=200)
def get_team_device_details(
    name: str,
    db: Session = Depends(get_db),
):
    """ Get device details """

    exist_device = crud.team_device.get_by_team_device_name(db, name)
    if not exist_device:
        raise HTTPException(status_code=404, detail=__("device-not-found"))

    return exist_device


@router.post("", response_model=schemas.TeamDevice, status_code=201)
def add_new_team_device(
    obj_in: schemas.TeamDeviceCreate = Body(...),    
    db: Session = Depends(get_db),
    current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    """ Add new team device: owner """

    exist_device = crud.team_device.get_by_team_device_name_for_nursery(db, obj_in.name, obj_in.nursery_uuid)
    if exist_device:
        raise HTTPException(status_code=409, detail=__("device-already-found"))

    device = crud.team_device.create(db=db, obj_in=schemas.TeamDeviceCreate(
        name=obj_in.name,
        nursery_uuid=obj_in.nursery_uuid
    ))

    return device

@router.put("", response_model=schemas.TeamDevice, status_code=200)
def update_team_device(
    obj_in: schemas.TeamDeviceUpdate = Body(...),
    db: Session = Depends(get_db),
    current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    """ Update device: owner """

    exist_device = crud.team_device.get_by_team_device_uuid(db, obj_in.uuid)
    if not exist_device:
        raise HTTPException(status_code=404, detail=__("device-not-found"))

    exist_device_name = crud.team_device.get_by_team_device_name_for_nursery(db, obj_in.name, obj_in.nursery_uuid)
    if exist_device_name and exist_device_name.uuid != exist_device.uuid:
        raise HTTPException(status_code=409, detail=__("device-already-found"))

    exist_device.name = obj_in.name if obj_in.name else exist_device.name
    db.commit()

    return exist_device

@router.get("", response_model=schemas.TeamDeviceList, status_code=200)
def get_many(
    *,
    nursery_uuid: str,
    page: int = 1,
    per_page: int = 30,
    order: str = Query("desc", enum=["asc", "desc"]),
    order_field: str = "date_added",
    keyword: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    """
    Get team device details: owner
    """
    return crud.team_device.get_many(
        db,
        nursery_uuid,
        page,
        per_page,
        order,
        order_field,
        keyword
    )

@router.get("/regenerate-code/{uuid}", response_model=schemas.TeamDevice, status_code=200)
def regenerate_team_device_code(
    uuid: str,
    db: Session = Depends(get_db),
    current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    """ Regenerate team device code: owner """

    exist_device = crud.team_device.get_by_team_device_uuid(db, uuid)
    if not exist_device:
        raise HTTPException(status_code=404, detail=__("device-not-found"))

    code = generate_code(length=15)
    exist_device.code = str(code)
    db.commit()

    return exist_device


@router.delete("/{uuid}", response_model=schemas.Msg, status_code=200)
def delete_team_device(
    uuid: str,
    db: Session = Depends(get_db),
    current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    """ Delete a team device: owner """

    crud.team_device.delete(db, uuids=[uuid])

    return {"message": __("team-device-deleted")}