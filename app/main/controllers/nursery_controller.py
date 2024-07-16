from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from app.main.core.config import Config
from fastapi import APIRouter, Depends, Body, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
router = APIRouter(prefix="/nurseries", tags=["nurseries"])


@router.post("/create", response_model=schemas.Nursery, status_code=201)
def create(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.NurseryCreate,
    current_user: models.Administrator = Depends(TokenRequired(roles=["administrator"]))
):
    """
    Create nursery
    """

    return crud.nursery.create(db, obj_in, current_user.uuid)


@router.put("/{uuid}", response_model=schemas.Nursery, status_code=200)
def update(
        uuid: str,
        obj_in: schemas.NurseryUpdateBase,
        db: Session = Depends(get_db),
        current_user: models.Administrator = Depends(TokenRequired(roles=["administrator"]))
):
    """
    Update nursery
    """
    nursery = crud.nursery.get(db=db, uuid=uuid)
    if not nursery:
        raise HTTPException(status_code=404, detail=__("nursery-not-found"))

    return crud.nursery.update(db, nursery, obj_in)


@router.put("/{uuid}/status", response_model=schemas.Nursery, status_code=200)
def update(
        uuid: str,
        status: str = Query(..., enum=[st.value for st in models.NurseryStatusType if
                                       st.value != models.NurseryStatusType.DELETED]),
        db: Session = Depends(get_db),
        current_user: models.Administrator = Depends(TokenRequired(roles=["administrator"]))
):
    """
    Update nursery owner status
    """
    nursery = crud.nursery.get(db=db, uuid=uuid)
    if not nursery:
        raise HTTPException(status_code=404, detail=__("nursery-not-found"))

    if nursery.status == status:
        return nursery

    return crud.nursery.update_status(db, nursery, status)


@router.get("/{uuid}", response_model=schemas.Nursery, status_code=200)
def get_details(
        uuid: str,
        db: Session = Depends(get_db),
        current_user: models.Administrator = Depends(TokenRequired(roles=["administrator"]))
):
    """
    Get nursery details
    """
    nursery = crud.nursery.get_by_uuid(db, uuid)
    if not nursery:
        raise HTTPException(status_code=404, detail=__("user-not-found"))

    return nursery


@router.delete("", response_model=schemas.Msg)
def delete(
        *,
        db: Session = Depends(get_db),
        uuids: list[str],
        current_user: models.Administrator = Depends(TokenRequired(roles=["administrator"]))
):
    """
    Delete many(or one)
    """
    crud.nursery.delete(db, uuids)
    return {"message": __("nursery-deleted")}


@router.get("/", response_model=schemas.NurseryList)
def get(
        *,
        db: Session = Depends(get_db),
        page: int = 1,
        per_page: int = 30,
        order: str = Query("desc", enum=["asc", "desc"]),
        order_filed: str = "date_added",
        keyword: Optional[str] = None,
        status: Optional[str] = Query(None, enum=[st.value for st in models.NurseryStatusType]),
        total_places: int = None,
        current_user: models.Administrator = Depends(TokenRequired(roles=["administrator"]))
):
    """
    get all with filters
    """

    return crud.nursery.get_multi(
        db,
        page,
        per_page,
        order,
        order_filed,
        keyword,
        status,
        total_places
    )
