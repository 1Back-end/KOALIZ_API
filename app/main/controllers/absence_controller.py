from app.main.core.dependencies import get_db, TeamTokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional


router = APIRouter(prefix="/absences", tags=["absences"])

@router.post("",response_model =schemas.Absence ,status_code=201)
def create_absence(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.AbsenceCreate,
    current_team_device: models.TeamDevice = Depends(TeamTokenRequired(roles=[]))

):
    """ Create absence for children """

    nursery = crud.nursery.get_by_uuid(db, obj_in.nursery_uuid)
    if not nursery:
        raise HTTPException(status_code=404, detail=__("nursery-not-found"))

    child = crud.preregistration.get_child_by_uuid(db, obj_in.child_uuid)
    if not child:
        raise HTTPException(status_code=404, detail=__("child-not-found"))

    employe = crud.employe.get_by_uuid(db, obj_in.employee_uuid)
    if not employe:
        raise HTTPException(status_code=404, detail=__("member-not-found"))

    return crud.absence.create(db, obj_in)


@router.put("", response_model=schemas.Absence, status_code=200)
def update_absence(
    obj_in: schemas.AbsenceUpdate,
    db: Session = Depends(get_db),
    current_team_device: models.TeamDevice = Depends(TeamTokenRequired(roles=[]))
):
    """ Update absence for children """

    absence = crud.absence.get_absence_by_uuid(db, obj_in.uuid)
    print("absence-updated",absence)
    if not absence:
        raise HTTPException(status_code=404, detail=__("absence-not-found"))

    child = crud.preregistration.get_child_by_uuid(db, obj_in.child_uuid)
    if not child:
        raise HTTPException(status_code=404, detail=__("child-not-found"))

    nursery = crud.nursery.get_by_uuid(db, obj_in.nursery_uuid)
    if not nursery:
        raise HTTPException(status_code=404, detail=__("nursery-not-found"))
    
    employe = crud.employe.get_by_uuid(db, obj_in.employee_uuid)
    if not employe:
        raise HTTPException(status_code=404, detail=__("member-not-found"))

    return crud.absence.update(db ,obj_in)


@router.delete("", response_model=schemas.Msg)
def delete_absence(
    *,
    db: Session = Depends(get_db),
    uuids: list[str],
    current_team_device: models.TeamDevice = Depends(TeamTokenRequired(roles =[]))
):
    """ Delete many(or one) """

    crud.absence.delete(db, uuids)
    return {"message": __("absence-deleted")}


@router.get("", response_model=None)
def get_absences(
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
    return crud.absence.get_multi(
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

@router.get("/{uuid}", response_model=schemas.Absence, status_code=200)
def get_absence_details(
        uuid: str,
        db: Session = Depends(get_db),
        current_team_device: models.TeamDevice = Depends(TeamTokenRequired(roles=[]))
):
    """ Get absence details """

    absence = crud.absence.get_absence_by_uuid(db, uuid)
    if not absence:
        raise HTTPException(status_code=404, detail=__("absence-not-found"))

    return absence
