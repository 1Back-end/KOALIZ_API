from app.main.core.dependencies import get_db, TeamTokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional


router = APIRouter(prefix="/activity_categories", tags=["activity_categories"])

@router.post("",response_model =schemas.ActivityCategory ,status_code=201)
def create_activity_category(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.ActivityCategoryCreate,
    current_team_device: models.TeamDevice = Depends(TeamTokenRequired(roles=[]))

):
    """ Create activity category """
    activity_type_errors = []

    if obj_in.activity_type_uuid_tab:
        for activity_type_uuid in obj_in.activity_type_uuid_tab:
            activity_type = crud.activity_category.get_activity_type_by_uuid(db, activity_type_uuid)
            if not activity_type:
                activity_type_errors.append(activity_type_uuid)
                # raise HTTPException(status_code=404, detail=__("activity-type-not-found"))
    
    if len(activity_type_errors)>0:
        raise HTTPException(status_code=404, detail=__("activity-type-not-found") +': '+"".join(activity_type_errors))
    
    return crud.activity_category.create(db, obj_in)


@router.put("", response_model=schemas.ActivityCategory, status_code=200)
def update_activity_category(
    obj_in: schemas.ActivityCategoryUpdate,
    db: Session = Depends(get_db),
    current_team_device: models.TeamDevice = Depends(TeamTokenRequired(roles=[]))
):
    """ Update activity categpory """

    exist_category_activity = crud.activity_category.get_activity_category_by_uuid(db, obj_in.uuid)
    if not exist_category_activity:
        raise HTTPException(status_code=404, detail=__("category-activity-not-found"))

    activity_type_errors = []

    if obj_in.activity_type_uuid_tab:
        for activity_type_uuid in obj_in.activity_type_uuid_tab:
            activity_type = crud.activity_category.get_activity_type_by_uuid(db, activity_type_uuid)
            if not activity_type:
                activity_type_errors.append(activity_type_uuid)
    
    if len(activity_type_errors)>0:
        raise HTTPException(status_code=404, detail=__("activity-type-not-found") +' '.join(activity_type_errors))
    
    return crud.activity_category.update(db ,obj_in)


@router.delete("", response_model=schemas.Msg)
def delete_activity_category(
    *,
    db: Session = Depends(get_db),
    uuids: list[str],
    current_team_device: models.TeamDevice = Depends(TeamTokenRequired(roles =[]))
):
    """ Delete many(or one) """

    crud.activity_category.delete(db, uuids)
    return {"message": __("category-activity-deleted-successfully")}


@router.get("", response_model=schemas.ActivityCategoryList)
def get_category_activities(
    *,
    db: Session = Depends(get_db),
    page: int = 1,
    per_page: int = 30,
    order: str = Query("desc", enum =["asc", "desc"]),
    order_field: str = "date_added",
    keyword: Optional[str] = None,
    current_team_device: models.TeamDevice = Depends(TeamTokenRequired(roles=[]))
):
    """
    get all with filters
    """
    return crud.activity_category.get_multi(
        db,
        page,
        per_page,
        order,
        order_field,
        keyword,
    )

@router.get("/{uuid}", response_model=schemas.ActivityCategory, status_code=201)
def get_activity_category_details(
        uuid: str,
        db: Session = Depends(get_db),
        current_team_device: models.TeamDevice = Depends(TeamTokenRequired(roles=[]))
):
    """ Get category activity details """

    activity_category = crud.activity_category.get_activity_category_by_uuid(db, uuid)
    if not activity_category:
        raise HTTPException(status_code=404, detail=__("category-activity-not-found"))

    return activity_category
