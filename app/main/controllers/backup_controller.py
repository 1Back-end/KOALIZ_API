from app.main.core.dependencies import get_db, TeamTokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional


router = APIRouter(prefix="/backups", tags=["backups"])

@router.post("/nap",response_model =schemas.Nap ,status_code=201)
def create_nap(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.NapCreate,
    current_team_device: models.TeamDevice = Depends(TeamTokenRequired(roles=[]))

):
    """ Create nap for children """

    child = crud.preregistration.get_child_by_uuid(db, obj_in.child_uuid)
    if not child:
        raise HTTPException(status_code=404, detail=__("child-not-found"))

    employe = crud.employe.get_by_uuid(db, obj_in.nursery_uuid)
    if not employe:
        raise HTTPException(status_code=404, detail=__("member-not-found"))

    return crud.nap.create(db, obj_in)


@router.put("/nap", response_model=schemas.Nap, status_code=200)
def update_nap(
    obj_in: schemas.NapUpdate,
    db: Session = Depends(get_db),
    current_user: models.Parent = Depends(TeamTokenRequired(roles=[]))
):
    """ Update nap for children """

    child = crud.preregistration.get_child_by_uuid(db, obj_in.child_uuid)
    if not child:
        raise HTTPException(status_code=404, detail=__("child-not-found"))

    nursery = crud.nursery.get_by_uuid(db, obj_in.nursery_uuid)
    if not nursery:
        raise HTTPException(status_code=404, detail=__("nursery-not-found"))

    return crud.parent.update(db ,obj_in)