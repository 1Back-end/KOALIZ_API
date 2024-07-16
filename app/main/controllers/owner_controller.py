from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from app.main.core.config import Config
from fastapi import APIRouter, Depends, Body, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
router = APIRouter(prefix="/owners", tags=["owners"])


@router.post("/create", response_model=schemas.Owner, status_code=201)
def create(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.OwnerCreate,
    current_user: models.User = Depends(TokenRequired(roles=["administrator"]))
):
    """
    Create owner
    """
    user = crud.owner.get_by_email(db, obj_in.email)
    if user:
        raise HTTPException(status_code=409, detail=__("user-email-taken"))

    if obj_in.avatar_uuid:
        avatar = crud.storage.get(db=db, uuid=obj_in.avatar_uuid)
        if not avatar:
            raise HTTPException(status_code=404, detail=__("avatar-not-found"))

    return crud.owner.create(db, obj_in, current_user.uuid)

@router.put("/{uuid}", response_model=schemas.Owner, status_code=201)
def update(
    uuid: str,
    obj_in: schemas.OwnerUpdateBase,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(TokenRequired(roles =["administrator"] ))
):
    """
    Update nursery owner
    """
    user = crud.owner.get_by_uuid(db, uuid)
    if not user:
        raise HTTPException(status_code=404, detail=__("user-not-found"))

    if obj_in.avatar_uuid and obj_in.avatar_uuid != user.avatar_uuid:
        if not crud.storage.get(db=db, uuid=obj_in.avatar_uuid):
            raise HTTPException(status_code=404, detail=__("avatar-not-found"))
        
    return crud.owner.update(db, user, obj_in)


@router.put("/{uuid}/status", response_model=schemas.Owner, status_code=201)
def update(
        uuid: str,
        status: str = Query(..., enum=[st.value for st in models.UserStatusType if st.value != models.UserStatusType.DELETED]),
        db: Session = Depends(get_db),
        current_user: models.User = Depends(TokenRequired(roles=["administrator"]))
):
    """
    Update nursery owner status
    """
    user = crud.owner.get_by_uuid(db, uuid)
    if not user:
        raise HTTPException(status_code=404, detail=__("user-not-found"))

    if user.status == status:
        return user

    return crud.owner.update(db, user, {"status": status})


@router.get("/{uuid}", response_model=schemas.Owner, status_code=201)
def get_details(
        uuid: str,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(TokenRequired(roles=["administrator"]))
):
    """
    Get nursery owner details
    """
    user = crud.owner.get_by_uuid(db, uuid)
    if not user:
        raise HTTPException(status_code=404, detail=__("user-not-found"))

    return user


@router.delete("", response_model=schemas.Msg)
def delete(
    *,
    db: Session = Depends(get_db),
    uuids: list[str],
    current_user: models.User = Depends(TokenRequired(roles =["administrator"]))
):
    """
    Delete many(or one)
    """
    crud.owner.delete(db, uuids)
    return {"message": __("user-deleted")}


@router.get("/", response_model=None)
def get(
    *,
    db: Session = Depends(get_db),
    page: int = 1,
    per_page: int = 30,
    order: str = Query("desc", enum =["asc", "desc"]),
    order_filed: str = "date_added",
    keyword: Optional[str] = None,
    current_user: models.User = Depends(TokenRequired(roles=["administrator"]))
):
    """
    get all with filters
    """
    
    return crud.owner.get_multi(
        db, 
        page, 
        per_page, 
        order, 
        order_filed,
        keyword
    )
    