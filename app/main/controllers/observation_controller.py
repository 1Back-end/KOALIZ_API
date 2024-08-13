from app.main.core.dependencies import get_db, TeamTokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional


router = APIRouter(prefix="/observations", tags=["observations"])

@router.post("",response_model =schemas.Observation ,status_code=201)
def create_observation(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.ObservationCreate,
    current_team_device: models.TeamDevice = Depends(TeamTokenRequired(roles=[]))

):
    """ Create observation for children """

    nursery = crud.nursery.get_by_uuid(db, obj_in.nursery_uuid)
    if not nursery:
        raise HTTPException(status_code=404, detail=__("nursery-not-found"))

    childs = crud.preregistration.get_child_by_uuids(db, obj_in.child_uuids)
    if not childs or len(childs)!=len(obj_in.child_uuids):
        raise HTTPException(status_code=404, detail=__("child-not-found"))

    employe = crud.employe.get_by_uuid(db, obj_in.employee_uuid)
    if not employe:
        raise HTTPException(status_code=404, detail=__("member-not-found"))

    return crud.observation.create(db, obj_in)


@router.put("", response_model=schemas.Observation, status_code=200)
def update_observation(
    obj_in: schemas.ObservationUpdate,
    db: Session = Depends(get_db),
    current_team_device: models.TeamDevice = Depends(TeamTokenRequired(roles=[]))
):
    """ Update observation for children """

    observation = crud.observation.get_observation_by_uuid(db, obj_in.uuid)
    if not observation:
        raise HTTPException(status_code=404, detail=__("observation-not-found"))

    childs = crud.preregistration.get_child_by_uuids(db, obj_in.child_uuids)
    if not childs or len(childs)!=len(obj_in.child_uuids):
        raise HTTPException(status_code=404, detail=__("child-not-found"))

    nursery = crud.nursery.get_by_uuid(db, obj_in.nursery_uuid)
    if not nursery:
        raise HTTPException(status_code=404, detail=__("nursery-not-found"))
    
    employe = crud.employe.get_by_uuid(db, obj_in.employee_uuid)
    if not employe:
        raise HTTPException(status_code=404, detail=__("member-not-found"))

    return crud.observation.update(db ,obj_in)


@router.delete("", response_model=schemas.Msg)
def delete_observation(
    *,
    db: Session = Depends(get_db),
    uuids: list[str],
    current_team_device: models.TeamDevice = Depends(TeamTokenRequired(roles =[]))
):
    """ Delete many(or one) """

    crud.observation.delete(db, uuids)
    return {"message": __("observation-deleted")}


@router.get("", response_model=None)
def get_observations(
    *,
    db: Session = Depends(get_db),
    page: int = 1,
    per_page: int = 30,
    order: str = Query("desc", enum =["asc", "desc"]),
    order_field: str = "date_added",
    employee_uuid: Optional[str] = None,
    nursery_uuid: Optional[str] = None,
    child_uuid: Optional[str] = None,
    keyword: Optional[str] = "",
    current_team_device: models.TeamDevice = Depends(TeamTokenRequired(roles=[]))
):
    """
    get all with filters
    """
    return crud.observation.get_multi(
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

@router.get("/{uuid}", response_model=schemas.Observation, status_code=201)
def get_observation_details(
        uuid: str,
        db: Session = Depends(get_db),
        current_team_device: models.TeamDevice = Depends(TeamTokenRequired(roles=[]))
):
    """ Get observation details """

    observation = crud.observation.get_observation_by_uuid(db, uuid)
    if not observation:
        raise HTTPException(status_code=404, detail=__("observation-not-found"))

    return observation
