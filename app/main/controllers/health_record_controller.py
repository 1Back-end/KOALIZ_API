from app.main.core.dependencies import get_db, TeamTokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional


router = APIRouter(prefix="/health_records", tags=["health_records"])

@router.post("",response_model =schemas.HealthRecord ,status_code=201)
def create_health_record(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.HealthRecordCreate,
    current_team_device: models.TeamDevice = Depends(TeamTokenRequired(roles=[]))

):
    """ Create health record for children """

    nursery = crud.nursery.get_by_uuid(db, obj_in.nursery_uuid)
    if not nursery:
        raise HTTPException(status_code=404, detail=__("nursery-not-found"))
    
    childs = crud.preregistration.get_child_by_uuids(db, obj_in.child_uuids)
    if not childs or len(childs)!= len(obj_in.child_uuids):
        raise HTTPException(status_code=404, detail=__("child-not-found"))

    employe = crud.employe.get_by_uuid(db, obj_in.employee_uuid)
    if not employe:
        raise HTTPException(status_code=404, detail=__("member-not-found"))

    return crud.health_record.create(db, obj_in)


@router.put("", response_model=schemas.HealthRecord, status_code=200)
def update_health_record(
    obj_in: schemas.HealthRecordUpdate,
    db: Session = Depends(get_db),
    current_team_device: models.TeamDevice = Depends(TeamTokenRequired(roles=[]))
):
    """ Update health record for children """

    health_record = crud.health_record.get_health_record_by_uuid(db, obj_in.uuid)
    if not health_record:
        raise HTTPException(status_code=404, detail=__("health-record-not-found"))

    childs = crud.preregistration.get_child_by_uuids(db, obj_in.child_uuids)
    if not childs or len(childs)!=len(obj_in.child_uuids):
        raise HTTPException(status_code=404, detail=__("child-not-found"))

    nursery = crud.nursery.get_by_uuid(db, obj_in.nursery_uuid)
    if not nursery:
        raise HTTPException(status_code=404, detail=__("nursery-not-found"))
    
    employe = crud.employe.get_by_uuid(db, obj_in.employee_uuid)
    if not employe:
        raise HTTPException(status_code=404, detail=__("member-not-found"))

    return crud.health_record.update(db ,obj_in)


@router.delete("", response_model=schemas.Msg)
def delete_health_record(
    *,
    db: Session = Depends(get_db),
    uuids: list[str],
    current_team_device: models.TeamDevice = Depends(TeamTokenRequired(roles =[]))
):
    """ Delete many(or one) """

    crud.health_record.delete(db, uuids)
    return {"message": __("health-record-deleted")}


@router.get("", response_model=None)
def get_health_records(
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
    route: str = Query(None, enum=[st.value for st in models.Route]),
    care_type: str = Query(None, enum=[st.value for st in models.CareType]),
    medication_type: str = Query(None, enum=[st.value for st in models.MedicationType]),
    current_team_device: models.TeamDevice = Depends(TeamTokenRequired(roles=[]))
):
    """
    get all with filters
    """
    return crud.health_record.get_multi(
        db,
        page,
        per_page,
        order,
        employee_uuid,
        nursery_uuid,
        child_uuid,
        order_field,
        keyword,
        route,
        care_type,
        medication_type
    )

@router.get("/{uuid}", response_model=schemas.HealthRecord, status_code=201)
def get_health_record_details(
        uuid: str,
        db: Session = Depends(get_db),
        current_team_device: models.TeamDevice = Depends(TeamTokenRequired(roles=[]))
):
    """ Get health record details """

    health_record = crud.health_record.get_health_record_by_uuid(db, uuid)
    if not health_record:
        raise HTTPException(status_code=404, detail=__("health-record-not-found"))

    return health_record
