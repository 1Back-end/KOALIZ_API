from app.main.core.dependencies import get_db, TeamTokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional


router = APIRouter(prefix="/attendances", tags=["attendances"])

@router.post("",response_model =schemas.Attendance ,status_code=201)
def create_attendance(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.AttendanceCreate,
    current_team_device: models.TeamDevice = Depends(TeamTokenRequired(roles=[]))

):
    """ Create attendance for children """

    nursery = crud.nursery.get_by_uuid(db, obj_in.nursery_uuid)
    if not nursery:
        raise HTTPException(status_code=404, detail=__("nursery-not-found"))

    childs = crud.preregistration.get_child_by_uuids(db, obj_in.child_uuid_tab)
    if not childs or len(childs)!=len(obj_in.child_uuid_tab):
        raise HTTPException(status_code=404, detail=__("child-not-found"))
    
    employe = crud.employe.get_by_uuid(db, obj_in.employee_uuid)
    if not employe:
        raise HTTPException(status_code=404, detail=__("member-not-found"))

    return crud.attendance.create(db, obj_in)


@router.put("", response_model=schemas.Attendance, status_code=200)
def update_attendance(
    obj_in: schemas.AttendanceUpdate,
    db: Session = Depends(get_db),
    current_team_device: models.TeamDevice = Depends(TeamTokenRequired(roles=[]))
):
    """ Update attendance for children """

    attendance = crud.attendance.get_attendance_by_uuid(db, obj_in.uuid)
    print("attendance-updated",attendance)
    if not attendance:
        raise HTTPException(status_code=404, detail=__("attendance-not-found"))

    childs = crud.preregistration.get_child_by_uuids(db, obj_in.child_uuid_tab)
    if not childs or len(childs)!=len(obj_in.child_uuid_tab):
        raise HTTPException(status_code=404, detail=__("child-not-found"))
    
    nursery = crud.nursery.get_by_uuid(db, obj_in.nursery_uuid)
    if not nursery:
        raise HTTPException(status_code=404, detail=__("nursery-not-found"))
    
    employe = crud.employe.get_by_uuid(db, obj_in.employee_uuid)
    if not employe:
        raise HTTPException(status_code=404, detail=__("member-not-found"))

    return crud.attendance.update(db ,obj_in)


@router.delete("", response_model=schemas.Msg)
def delete_attendance(
    *,
    db: Session = Depends(get_db),
    uuids: list[str],
    current_team_device: models.TeamDevice = Depends(TeamTokenRequired(roles =[]))
):
    """ Delete many(or one) """

    crud.attendance.soft_delete(db, uuids)
    return {"message": __("attendance-deleted")}


@router.get("", response_model=None)
def get_attendances(
    *,
    db: Session = Depends(get_db),
    page: int = 1,
    per_page: int = 30,
    order: str = Query("desc", enum =["asc", "desc"]),
    order_field: str = "date_added",
    employee_uuid: Optional[str] = None,
    nursery_uuid: Optional[str] = None,
    child_uuid: Optional[str] = None,
    # keyword: Optional[str] = None,
    current_team_device: models.TeamDevice = Depends(TeamTokenRequired(roles=[]))
):
    """
    get all with filters
    """
    return crud.attendance.get_multi(
        db,
        page,
        per_page,
        order,
        employee_uuid,
        nursery_uuid,
        child_uuid,
        order_field
    )

@router.get("/{uuid}", response_model=schemas.Attendance, status_code=201)
def get_attendance_details(
        uuid: str,
        db: Session = Depends(get_db),
        current_team_device: models.TeamDevice = Depends(TeamTokenRequired(roles=[]))
):
    """ Get attendance details """

    attendance = crud.attendance.get_attendance_by_uuid(db, uuid)
    if not attendance:
        raise HTTPException(status_code=404, detail=__("attendance-not-found"))

    return attendance
