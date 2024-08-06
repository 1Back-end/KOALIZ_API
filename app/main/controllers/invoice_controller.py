from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.main import schemas, crud, models
from app.main.core.dependencies import get_db, TokenRequired
from app.main.core.i18n import __


router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.get("/", response_model=schemas.InvoiceList)
def get(
        nursery_uuid: str,
        db: Session = Depends(get_db),
        page: int = 1,
        per_page: int = 30,
        order: str = Query("desc", enum=["asc", "desc"]),
        order_filed: str = "date_to",
        keyword: Optional[str] = None,
        status: Optional[str] = Query(None, enum=models.InvoiceStatusType),
        month: Optional[int] = None,
        year: Optional[int] = None,
        reference: Optional[str] = None,
        child_uuid: Optional[str] = None,
        current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    """
    get all with filters
    """
    return crud.invoice.get_many(
        db,
        nursery_uuid,
        current_user.uuid,
        page,
        per_page,
        order,
        order_filed,
        keyword,
        status,
        reference
    )


@router.get("/{uuid}", response_model=schemas.InvoiceDetails, status_code=200, include_in_schema=False)
def get_details(
        uuid: str,
        db: Session = Depends(get_db),
        current_user=Depends(TokenRequired(roles=["owner"]))
):
    """
        Get quote details
    """
    quote = crud.quote.get_by_uuid(db, uuid)
    if not quote:
        raise HTTPException(status_code=404, detail=__("quote-not-found"))

    if current_user.role.code == "owner" and quote.nursery.owner_uuid != current_user.uuid:
        raise HTTPException(status_code=404, detail=__("quote-not-found"))

    return quote
