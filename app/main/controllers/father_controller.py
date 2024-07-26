from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional


router = APIRouter(prefix="/fathers", tags=["fathers"])


@router.put("", response_model=schemas.Father, status_code=201)
def update(
    obj_in: schemas.FatherUpdate,
    db: Session = Depends(get_db),
    current_user: models.Father = Depends(TokenRequired(roles =["father"] ))
):
    """
    Update father
    """
    user = crud.father.get_by_uuid(db, obj_in.uuid)
    if not user:
        raise HTTPException(status_code=404, detail=__("user-not-found"))

    if obj_in.avatar_uuid and obj_in.avatar_uuid != user.avatar_uuid:
        if not crud.storage.get(db=db, uuid=obj_in.avatar_uuid):
            raise HTTPException(status_code=404, detail=__("avatar-not-found"))

    return crud.father.update(db, user, obj_in)


@router.put("/status", response_model=schemas.Father, status_code=201)
def update(
    *,
        uuid: str,
        status: str = Query(..., enum=[st.value for st in models.UserStatusType if st.value != models.UserStatusType.DELETED]),
        db: Session = Depends(get_db),
        current_user: models.Father = Depends(TokenRequired(roles=["father"]))
):
    """
    Update father status
    """
    user = crud.father.get_by_uuid(db, uuid)
    if not user:
        raise HTTPException(status_code=404, detail=__("user-not-found"))

    if user.status == status:
        return user

    return crud.father.update(db, user, {"status": status})


@router.get("/{uuid}", response_model=schemas.Father, status_code=201)
def get_details(
        uuid: str,
        db: Session = Depends(get_db),
        current_user: models.Father = Depends(TokenRequired(roles=["father"]))
):
    """
    Get father details
    """
    user = crud.father.get_by_uuid(db, uuid)
    if not user:
        raise HTTPException(status_code=404, detail=__("user-not-found"))

    return user


@router.delete("", response_model=schemas.Msg)
def delete(
    *,
    db: Session = Depends(get_db),
    uuids: list[str],
    current_user: models.Father = Depends(TokenRequired(roles =["father"]))
):
    """
    Delete many(or one)
    """
    crud.father.delete(db, uuids)
    return {"message": __("user-deleted")}


@router.get("", response_model=None)
def get(
    *,
    db: Session = Depends(get_db),
    page: int = 1,
    per_page: int = 30,
    order: str = Query("desc", enum =["asc", "desc"]),
    order_filed: str = "date_added",
    keyword: Optional[str] = None,
    current_user: models.Father = Depends(TokenRequired(roles=["father"]))
):
    """
    get all with filters
    """
    return crud.father.get_multi(
        db,
        page,
        per_page,
        order,
        order_filed,
        keyword
    )
