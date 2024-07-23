from datetime import time, date

from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from app.main.core.config import Config
from fastapi import APIRouter, Depends, Body, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional


router = APIRouter(prefix="/pre-registrations", tags=["pre-registrations"])


@router.post("/create", response_model=schemas.ChildDetails, status_code=201)
def create(
    *,
    db: Session = Depends(get_db),
    obj_in: schemas.PreregistrationCreate,
):
    """
    Create preregistration
    """

    return crud.preregistration.create(db, obj_in, "dfd")


@router.get("/{child_uuid}", response_model=schemas.ChildDetails, status_code=200)
def get_details(
        child_uuid: str,
        db: Session = Depends(get_db),
        current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    """
    Get nursery details
    """
    return crud.preregistration.get_child_by_uuid(db, child_uuid)


@router.get("", response_model=schemas.PreRegistrationList, status_code=200)
def get_many(
        nursery_uuid: str,
        tag_uuid: str = None,
        status: str = None,
        begin_date: date = None,
        end_date: date = date.today(),
        page: int = 1,
        per_page: int = 30,
        order: str = Query("desc", enum=["asc", "desc"]),
        order_field: str = "date_added",
        keyword: Optional[str] = None,
        db: Session = Depends(get_db),
        current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    """
    Get nursery details
    """
    return crud.preregistration.get_many(
        db,
        nursery_uuid,
        tag_uuid,
        status,
        begin_date,
        end_date,
        page,
        per_page,
        order,
        order_field,
        keyword
    )
