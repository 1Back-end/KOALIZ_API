from app.main.core.dependencies import get_db, TeamTokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional


router = APIRouter(prefix="/occasional_presences", tags=["occasional_presences"])

@router.post("",response_model =schemas.OccasionalPresence ,status_code=201)
def create_occasional_presence(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.OccasionalPresenceCreate,
    current_team_device: models.TeamDevice = Depends(TeamTokenRequired(roles=[]))

):
    """ Create occasional presence for children """

    if obj_in.nursery_uuid:
        nursery = crud.nursery.get_by_uuid(db, obj_in.nursery_uuid)
        if not nursery:
            raise HTTPException(status_code=404, detail=__("nursery-not-found"))
    
    if obj_in.child_uuid:
        child = crud.preregistration.get_child_by_uuid(db, obj_in.child_uuid)
        if not child:
            raise HTTPException(status_code=404, detail=__("child-not-found"))

    if obj_in.employee_uuid:
        employe = crud.employe.get_by_uuid(db, obj_in.employee_uuid)
        if not employe:
            raise HTTPException(status_code=404, detail=__("member-not-found"))

    return crud.occasional_presence.create(db, obj_in)


@router.put("", response_model=schemas.OccasionalPresence, status_code=200)
def update_occasional_presence(
    obj_in: schemas.OccasionalPresenceUpdate,
    db: Session = Depends(get_db),
    current_team_device: models.TeamDevice = Depends(TeamTokenRequired(roles=[]))
):
    """ Update occasional presence for children """

    occasional_presence = crud.occasional_presence.get_occasional_presence_by_uuid(db, obj_in.uuid)
    print("occasional_presence-updated",occasional_presence)
    if not occasional_presence:
        raise HTTPException(status_code=404, detail=__("occasional-presence-not-found"))

    if obj_in.child_uuid:
        child = crud.preregistration.get_child_by_uuid(db, obj_in.child_uuid)
        if not child:
            raise HTTPException(status_code=404, detail=__("child-not-found"))
    
    if obj_in.nursery_uuid:
        nursery = crud.nursery.get_by_uuid(db, obj_in.nursery_uuid)
        if not nursery:
            raise HTTPException(status_code=404, detail=__("nursery-not-found"))
    
    if obj_in.employee_uuid:
        employe = crud.employe.get_by_uuid(db, obj_in.employee_uuid)
        if not employe:
            raise HTTPException(status_code=404, detail=__("member-not-found"))

    return crud.occasional_presence.update(db ,obj_in)


@router.delete("", response_model=schemas.Msg)
def delete_occasional_presence(
    *,
    db: Session = Depends(get_db),
    uuids: list[str],
    current_team_device: models.TeamDevice = Depends(TeamTokenRequired(roles =[]))
):
    """ Delete many(or one) """

    crud.occasional_presence.delete(db, uuids)
    return {"message": __("occasional-presence-deleted")}


@router.get("", response_model=None)
def get_occasional_presences(
    *,
    db: Session = Depends(get_db),
    page: int = 1,
    per_page: int = 30,
    order: str = Query("desc", enum =["asc", "desc"]),
    order_field: str = "date_added",
    employee_uuid: Optional[str] = None,
    nursery_uuid: Optional[str] = None,
    child_uuid: Optional[str] = None,
    keyword: Optional[str] = None,
    current_team_device: models.TeamDevice = Depends(TeamTokenRequired(roles=[]))
):
    """
    get all with filters
    """
    return crud.occasional_presence.get_multi(
        db,
        page,
        per_page,
        order,
        employee_uuid,
        nursery_uuid,
        child_uuid,
        order_field,
        keyword
    )

@router.get("/{uuid}", response_model=schemas.OccasionalPresence, status_code=201)
def get_occasional_presence_details(
        uuid: str,
        db: Session = Depends(get_db),
        current_team_device: models.TeamDevice = Depends(TeamTokenRequired(roles=[]))
):
    """ Get occasional presence details """

    occasional_presence = crud.occasional_presence.get_occasional_presence_by_uuid(db, uuid)
    if not occasional_presence:
        raise HTTPException(status_code=404, detail=__("occasional-presence-not-found"))

    return occasional_presence
