from app.main.core.dependencies import get_db, TeamTokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional,List


router = APIRouter(prefix="/children_activities", tags=["children_activities"])

@router.post("",response_model =schemas.ChildActivityDetails ,status_code=201)
def create_child_activity(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.ChildActivityCreate,
    current_team_device: models.TeamDevice = Depends(TeamTokenRequired(roles=[]))

):
    """ Create child_activity for children """

    nursery = crud.nursery.get_by_uuid(db, obj_in.nursery_uuid)
    if not nursery:
        raise HTTPException(status_code=404, detail=__("nursery-not-found"))

    childs = crud.preregistration.get_child_by_uuids(db, obj_in.child_uuids)
    if not childs or len(childs)!= len(obj_in.child_uuids):
        raise HTTPException(status_code=404, detail=__("child-not-found"))

    employe = crud.employe.get_by_uuid(db, obj_in.employee_uuid)
    if not employe:
        raise HTTPException(status_code=404, detail=__("member-not-found"))

    return crud.child_activity.create(db, obj_in)


@router.put("", response_model=schemas.ChildActivityDetails, status_code=200)
def update_child_activity(
    obj_in: schemas.ChildActivityUpdate,
    db: Session = Depends(get_db),
    current_team_device: models.TeamDevice = Depends(TeamTokenRequired(roles=[]))
):
    """ Update child_activity for children """

    child_activity = crud.child_activity.get_by_activity_uuid_and_child_uuid(db, obj_in.uuid)
    if not child_activity:
        raise HTTPException(status_code=404, detail=__("child-activity-not-found"))

    # childs = crud.preregistration.get_child_by_uuids(db, obj_in.child_uuids)
    # if not childs or len(childs)!=len(obj_in.child_uuids):
    #     raise HTTPException(status_code=404, detail=__("child-not-found"))

    # nursery = crud.nursery.get_by_uuid(db, obj_in.nursery_uuid)
    # if not nursery:
    #     raise HTTPException(status_code=404, detail=__("nursery-not-found"))
    
    # employe = crud.employe.get_by_uuid(db, obj_in.employee_uuid)
    # if not employe:
    #     raise HTTPException(status_code=404, detail=__("member-not-found"))

    return crud.child_activity.update(db ,obj_in)


@router.delete("", response_model=schemas.Msg)
def delete_child_activity(
    *,
    db: Session = Depends(get_db),
    uuids: list[str],
    current_team_device: models.TeamDevice = Depends(TeamTokenRequired(roles =[]))
):
    """ Delete many(or one) """

    crud.child_activity.delete(db, uuids)
    return {"message": __("child-activity-deleted")}


@router.get("", response_model=None)
def get_child_activitys(
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
    return crud.child_activity.get_multi(
        db,
        page,
        per_page,
        order,
        employee_uuid,
        nursery_uuid,
        child_uuid,
        order_field
    )

@router.get("/{uuid}", response_model=schemas.ChildActivityDetails, status_code=200)
def get_child_activity_details(
    activity_uuid: str,
    child_uuid: str,
    db: Session = Depends(get_db),
    current_team_device: models.TeamDevice = Depends(TeamTokenRequired(roles=[]))
):
    """ Get child_activity details """

    child_activity = crud.child_activity.get_by_activity_uuid_and_child_uuid(db, activity_uuid,child_uuid)
    if not child_activity:
        raise HTTPException(status_code=404, detail=__("child-activity-not-found"))

    return child_activity
