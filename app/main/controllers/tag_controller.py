from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from app.main.core.config import Config
from fastapi import APIRouter, Depends, Body, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional


router = APIRouter(prefix="/tags", tags=["tags"])

@router.post("/create", response_model=schemas.Tag, status_code=201)
def create(
    *,
    db: Session = Depends(get_db),
    obj_in:schemas.TagCreate,
    current_user:models.Administrator = Depends(TokenRequired(roles =["owner"]))
):
    """
    Create new Tag
    """
    if obj_in.icon_uuid:
        icon = crud.storage.get(db,obj_in.icon_uuid)
        if not icon:
            raise HTTPException(status_code=404, detail=__("file-not-found"))

    tag = crud.tag.get_title(db,obj_in.title_fr,obj_in.title_en)
    if tag:
        raise HTTPException(status_code=409, detail=__("tag-title-taken"))

    return crud.tag.create(db, obj_in)

@router.put("/update", response_model=schemas.Tag, status_code=201)
def update(
    *,
    db: Session = Depends(get_db),
    obj_in:schemas.TagUpdate,
    current_user:models.Administrator = Depends(TokenRequired(roles =["administrator"]))
):
    """
    update a Tag
    """
    if obj_in.icon_uuid:
        icon = crud.storage.get(db,obj_in.icon_uuid)
        if not icon:
            raise HTTPException(status_code=404, detail=__("file-not-found"))
    print("1112",obj_in.title_en,obj_in.title_fr)

    if obj_in.title_en or obj_in.title_fr:
        tag = crud.tag.get_title(db,obj_in.title_fr,obj_in.title_en)
        if tag and tag.uuid!= obj_in.uuid:
            raise HTTPException(status_code=409, detail=__("tag-title-taken"))


    return crud.tag.update(db, obj_in)

@router.delete("/delete", response_model=schemas.Msg, status_code=200)
def delete(
    *,
    db: Session = Depends(get_db),
    obj_in:schemas.TagDelete,
    current_user:models.Administrator = Depends(TokenRequired(roles =["administrator"]))
):
    """
    delete a Tag
    """

    if not crud.tag.get_by_uuids(db, obj_in.uuids):
        raise HTTPException(status_code=404, detail=__("tag-not-found"))
    
    crud.tag.delete(db, obj_in.uuids)

    return {"message":__("tag-deleted")}

# @router.post("/update", response_model=schemas.Tag, status_code=201)
# def update(
#     *,
#     db: Session = Depends(get_db),
#     obj_in:schemas.TagUpdate,
#     current_user:models.Administrator = Depends(TokenRequired(roles =["administrator"]))
# ):
#     """
#     update a Tag
#     """
#     if obj_in.icon_uuid:
#         icon = crud.storage.get(db,obj_in.icon_uuid)
#         if not icon:
#             raise HTTPException(status_code=404, detail=__("file-not-found"))

#     return crud.tag.update(db, obj_in)

@router.get("/", response_model=schemas.TagsResponseList)
def get(
    *,
    db: Session = Depends(get_db),
    page: int = 1,
    per_page: int = 30,
    order:str = Query(None, enum =["ASC","DESC"]),
    title: Optional[str] = None,
    color:Optional[str] = None,
    type:Optional[str] = None,
    icon_uuid:Optional[str] = None,
    uuid:Optional[str] = None,
    # order_filed: Optional[str] = None
    current_user: models.Administrator = Depends(TokenRequired(roles =["administrator"] ))
):
    """
    get tags with all data by passing filters
    """
    if icon_uuid:
        icon = crud.storage.get(db,icon_uuid)
        if not icon:
            raise HTTPException(status_code=404, detail=__("file-not-found"))

    return crud.tag.get_multi(
        db, 
        page, 
        per_page, 
        order,
        title,
        color,
        type,
        icon_uuid
        # order_filed
    )