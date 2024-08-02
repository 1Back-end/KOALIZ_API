from datetime import time

from app.main.core.dependencies import get_db, TokenRequired
from app.main import schemas, crud, models
from app.main.core.i18n import __
from app.main.core.config import Config
from fastapi import APIRouter, Depends, Body, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional


router = APIRouter(prefix="/quotes", tags=["quotes"])


@router.get("/{uuid}", response_model=schemas.QuoteDetails, status_code=200, include_in_schema=False)
def get_details(
        uuid: str,
        db: Session = Depends(get_db),
        current_user=Depends(TokenRequired(roles=["administrator", "owner"]))
):
    """
    Get nursery details
    """
    nursery = crud.nursery.get_by_uuid(db, uuid)
    if not nursery:
        raise HTTPException(status_code=404, detail=__("nursery-not-found"))

    if current_user.role.code == "owner" and nursery.owner_uuid != current_user.uuid:
        raise HTTPException(status_code=404, detail=__("nursery-not-found"))

    return nursery


@router.get("/", response_model=schemas.QuoteList)
def get(
        nursery_uuid: str,
        db: Session = Depends(get_db),
        page: int = 1,
        per_page: int = 30,
        order: str = Query("desc", enum=["asc", "desc"]),
        order_filed: str = "date_added",
        keyword: Optional[str] = None,
        status: Optional[str] = Query(None, enum=[st.value for st in models.NurseryStatusType]),
        current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    """
    get all with filters
    """
    return crud.quote.get_many(
        db,
        nursery_uuid,
        current_user.uuid,
        page,
        per_page,
        order,
        order_filed,
        keyword,
        status
    )

