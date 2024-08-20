from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
router = APIRouter(prefix="/owners", tags=["owners"])



@router.post("/children-confirmation", response_model=schemas.ChildMini, status_code=201)
def confirm_child_for_parent(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.ChildrenConfirmation = Body(...),
    current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    """ Confirm child for parent """

    if not obj_in.nursery_uuid  in [current_nursery.uuid for current_nursery in current_user.nurseries]:
        raise HTTPException(status_code = 400,detail = __("nursery-owner-not-authorized"))
    
    nursery = crud.nursery.get_by_uuid(db, obj_in.nursery_uuid)
    if not nursery:
        raise HTTPException(status_code=404, detail=__("nursery-not-found"))

    child = crud.preregistration.get_child_by_uuid(db, obj_in.child_uuid)
    if not child:
        raise HTTPException(status_code=404, detail=__("child-not-found"))
    
    parent = db.query(models.Parent).filter(models.Parent.email.ilike(obj_in.parent_email)).first()
    if not parent:
        raise HTTPException(status_code=404, detail=__("user-not-found"))

    crud.administrator.confirm_child_for_parent(db=db, obj_in=obj_in, added_by=current_user)

    return child

@router.post("/create", response_model=schemas.Owner, status_code=201)
def create(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.OwnerCreate,
    current_user: models.Administrator = Depends(TokenRequired(roles=["administrator"]))
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
    current_user: models.Administrator = Depends(TokenRequired(roles =["administrator"] ))
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
        current_user: models.Administrator = Depends(TokenRequired(roles=["administrator"]))
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
        current_user: models.Administrator = Depends(TokenRequired(roles=["administrator"]))
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
    current_user: models.Administrator = Depends(TokenRequired(roles =["administrator"]))
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
    current_user: models.Administrator = Depends(TokenRequired(roles=["administrator"]))
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
    