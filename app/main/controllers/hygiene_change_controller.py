from app.main.core.dependencies import get_db, TeamTokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional


router = APIRouter(prefix="/hygiene_changes", tags=["hygiene_changes"])

@router.post("",response_model =schemas.HygieneChange ,status_code=201)
def create_hygiene_change(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.HygieneChangeCreate,
    current_team_device: models.TeamDevice = Depends(TeamTokenRequired(roles=[]))

):
    """ Create hygiene change for children """

    nursery = crud.nursery.get_by_uuid(db, obj_in.nursery_uuid)
    if not nursery:
        raise HTTPException(status_code=404, detail=__("nursery-not-found"))

    childs = crud.preregistration.get_child_by_uuids(db, obj_in.child_uuids)
    if not childs or len(childs)!=len(childs):
        raise HTTPException(status_code=404, detail=__("child-not-found"))

    employe = crud.employe.get_by_uuid(db, obj_in.employee_uuid)
    if not employe:
        raise HTTPException(status_code=404, detail=__("member-not-found"))

    return crud.hygiene_change.create(db, obj_in)


@router.put("", response_model=schemas.HygieneChange, status_code=200)
def update_hygiene_change(
    obj_in: schemas.HygieneChangeUpdate,
    db: Session = Depends(get_db),
    current_team_device: models.TeamDevice = Depends(TeamTokenRequired(roles=[]))
):
    """ Update hygiene change for children """

    hygiene_change = crud.hygiene_change.get_hygiene_change_by_uuid(db, obj_in.uuid)
    if not hygiene_change:
        raise HTTPException(status_code=404, detail=__("hygiene-change-not-found"))

    childs = crud.preregistration.get_child_by_uuids(db, obj_in.child_uuids)
    if not childs or len(childs)!= len(obj_in.child_uuids):
        raise HTTPException(status_code=404, detail=__("child-not-found"))

    nursery = crud.nursery.get_by_uuid(db, obj_in.nursery_uuid)
    if not nursery:
        raise HTTPException(status_code=404, detail=__("nursery-not-found"))
    
    employe = crud.employe.get_by_uuid(db, obj_in.employee_uuid)
    if not employe:
        raise HTTPException(status_code=404, detail=__("member-not-found"))

    return crud.hygiene_change.update(db ,obj_in)


@router.delete("", response_model=schemas.Msg)
def delete_hygiene_change(
    *,
    db: Session = Depends(get_db),
    uuids: list[str],
    current_team_device: models.TeamDevice = Depends(TeamTokenRequired(roles =[]))
):
    """ Delete many(or one) """

    crud.hygiene_change.soft_delete(db, uuids)
    return {"message": __("hygiene-change-deleted")}


@router.get("", response_model=None)
def get_hygiene_changes(
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
    cleanliness: str = Query(None, enum=[st.value for st in models.Cleanliness]),
    stool_type: str = Query(None, enum=[st.value for st in models.StoolType]),
    additional_care: str = Query(None, enum=[st.value for st in models.AdditionalCare]),
    current_team_device: models.TeamDevice = Depends(TeamTokenRequired(roles=[]))
):
    """
    get all with filters
    """
    return crud.hygiene_change.get_multi(
        db,
        page,
        per_page,
        order,
        employee_uuid,
        nursery_uuid,
        child_uuid,
        order_field,
        keyword,
        cleanliness,
        stool_type,
        additional_care
    )

@router.get("/{uuid}", response_model=schemas.HygieneChange, status_code=201)
def get_hygiene_change_details(
        uuid: str,
        db: Session = Depends(get_db),
        current_team_device: models.TeamDevice = Depends(TeamTokenRequired(roles=[]))
):
    """ Get hygiene change details """

    hygiene_change = crud.hygiene_change.get_hygiene_change_by_uuid(db, uuid)
    if not hygiene_change:
        raise HTTPException(status_code=404, detail=__("hygiene-change-not-found"))

    return hygiene_change
