from app.main.core.dependencies import get_db, TeamTokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional


router = APIRouter(prefix="/medias", tags=["medias"])

@router.post("",response_model =schemas.Media ,status_code=201)
def create_media(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.MediaCreate,
    current_team_device: models.TeamDevice = Depends(TeamTokenRequired(roles=[]))

):
    """ Create media for children """

    nursery = crud.nursery.get_by_uuid(db, obj_in.nursery_uuid)
    if not nursery:
        raise HTTPException(status_code=404, detail=__("nursery-not-found"))

    childs = crud.preregistration.get_child_by_uuids(db, obj_in.child_uuids)
    if not childs or  len(obj_in.child_uuids)!= len(childs):
        raise HTTPException(status_code=404, detail=__("child-not-found"))

    employe = crud.employe.get_by_uuid(db, obj_in.employee_uuid)
    if not employe:
        raise HTTPException(status_code=404, detail=__("member-not-found"))

    return crud.media.create(db, obj_in)


@router.put("", response_model=schemas.Media, status_code=200)
def update_media(
    obj_in: schemas.MediaUpdate,
    db: Session = Depends(get_db),
    current_team_device: models.TeamDevice = Depends(TeamTokenRequired(roles=[]))
):
    """ Update media for children """
    
    if current_team_device.nursery_uuid!=obj_in.nursery_uuid:
        raise HTTPException(status_code=403, detail=__("not-authorized"))

    media = crud.media.get_media_by_uuid(db, obj_in.uuid)
    print("media-updated",media)
    if not media:
        raise HTTPException(status_code=404, detail=__("media-not-found"))

    childs = crud.preregistration.get_child_by_uuids(db, obj_in.child_uuids)
    if not childs or  len(obj_in.child_uuids)!= len(childs):
        raise HTTPException(status_code=404, detail=__("child-not-found"))

    nursery = crud.nursery.get_by_uuid(db, obj_in.nursery_uuid)
    if not nursery:
        raise HTTPException(status_code=404, detail=__("nursery-not-found"))
    
    employe = crud.employe.get_by_uuid(db, obj_in.employee_uuid)
    if not employe:
        raise HTTPException(status_code=404, detail=__("member-not-found"))
    
    if employe not in current_team_device.members:
        raise HTTPException(status_code=403, detail=__("not-authorized"))
    
    return crud.media.update(db ,obj_in)


@router.delete("", response_model=schemas.Msg)
def delete_media(
    *,
    db: Session = Depends(get_db),
    uuids: list[str],
    current_team_device: models.TeamDevice = Depends(TeamTokenRequired(roles =[]))
):
    """ Delete many(or one) """
    
    nursery_media =  db.query(models.Media).\
        filter(models.Media.uuid.in_(uuids)).\
        filter(models.Media.nursery_uuid ==current_team_device.nursery_uuid).\
        all()
    
    if not nursery_media or len(nursery_media)!=len(uuids):
        raise HTTPException(status_code=404, detail=__("media-not-found"))

    crud.media.delete(db, uuids)
    return {"message": __("media-deleted")}


@router.get("", response_model=None)
def get_medias(
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
    media_type: str = Query(None, enum=[st.value for st in models.MediaType]),
    current_team_device: models.TeamDevice = Depends(TeamTokenRequired(roles=[]))
):
    """
    get all with filters
    """
    return crud.media.get_multi(
        db,
        page,
        per_page,
        order,
        employee_uuid,
        nursery_uuid,
        child_uuid,
        order_field,
        keyword,
        media_type
    )

@router.get("/{uuid}", response_model=schemas.Media, status_code=201)
def get_media_details(
        uuid: str,
        db: Session = Depends(get_db),
        current_team_device: models.TeamDevice = Depends(TeamTokenRequired(roles=[]))
):
    """ Get media details """

    media = crud.media.get_media_by_uuid(db, uuid)
    if not media:
        raise HTTPException(status_code=404, detail=__("media-not-found"))

    return media
