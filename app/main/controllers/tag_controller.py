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
    current_user:models.Administrator = Depends(TokenRequired(roles =["administrator"]))
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

@router.put("/update-tag-of-element", response_model=schemas.Msg, status_code=201)
def update_tag_element(
    *,
    db: Session = Depends(get_db),
    obj_in:schemas.TagElementUpdate,
    current_user:models.Administrator = Depends(TokenRequired(roles =[]))
):
    """
    update a 
    """
    tag = db.query(models.TagElement).filter(models.TagElement.uuid==obj_in.uuid).first()
    
    if not tag:
        raise HTTPException(status_code=404, detail=__("tag-not-found"))
    
    if not  crud.tag.get_tag_by_element(db,tag.tag_uuid,obj_in.element_uuid,obj_in.element_type):
        tag.element_uuid = obj_in.element_uuid if obj_in.element_uuid else tag.element_uuid
        tag.element_type = obj_in.element_type if obj_in.element_type else tag.element_type
        tag.tag_uuid = obj_in.tag_uuid if obj_in.tag_uuid else tag.tag_uuid

    db.commit()
    
    return {"message":__("tag-updated")}



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

@router.post("/add-tag-to-element", response_model=schemas.Msg, status_code=201)
def add_tag_to_element(
    *,
    db: Session = Depends(get_db),
    obj_in:schemas.TagElementCreate,
    current_user:models.User = Depends(TokenRequired(roles =[]))
):
    """
    update a Tag
    """
    tags = crud.tag.get_by_uuids(db, obj_in.tag_uuids)
    print("tags1",tags)
    if not tags:
        raise HTTPException(status_code=404, detail=__("tag-not-found"))
    if len(tags)>1:
        for tag in tags:
            if not crud.tag.get_tag_by_element(db,tag.uuid,obj_in.element_uuid,obj_in.element_type):
                crud.tag.add_tag_to_element(db,obj_in)
    # else:
    #     if not crud.tag.get_tag_by_element(db,tags.uuid,obj_in.element_uuid,obj_in.element_type):
    #             crud.tag.add_tag_to_element(db,obj_in)

    return {"message":__("Ok")}


@router.delete("/remove_tag_from_element", response_model=schemas.Msg, status_code=201)
def remove_tag_from_element(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.TagElementDelete,
    current_user: models.User = Depends(TokenRequired(roles =[]))
):
    """
    remove a Tag
    """
    tags = crud.tag.get_by_uuids(db, obj_in.uuids)

    if not tags:
        raise HTTPException(status_code=404, detail=__("tag-not-found"))
    
    crud.tag.delete_tag_from_element(db,obj_in)

    return {"message":__("tag-deleted")}


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

@router.get("/elements", response_model=schemas.TagElementResponseList)
def get(
    *,
    db: Session = Depends(get_db),
    page: int = 1,
    per_page: int = 30,
    order:str = Query(None, enum =["ASC","DESC"]),
    uuid:Optional[str] = None,
    type:Optional[str] = Query(None, enum =["CHILDREN","TEAM","PARENTS","DOCUMENTS","PRE_ENROLLMENT","PICTURE","BILL"]),
    # order_filed: Optional[str] = None
    current_user: models.Administrator = Depends(TokenRequired(roles =["administrator"] ))
):
    """
    get tags with all data by passing filters
    """
    if uuid:
        tag = crud.tag.get_tag_element(db,uuid)
        if not tag:
            raise HTTPException(status_code=404, detail=__("tag-not-found"))
    

    return crud.tag.get_multi_by_element(
        db, 
        page, 
        per_page, 
        order,
        uuid,
        type
        # order_filed
    )
    