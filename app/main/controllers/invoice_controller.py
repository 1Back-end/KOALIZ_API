from datetime import date

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
        order: str = Query("asc", enum=["asc", "desc"]),
        order_filed: str = "date_to",
        keyword: Optional[str] = None,
        status: Optional[str] = Query(None, enum=[st.value for st in models.InvoiceStatusType]),
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
        db=db, nursery_uuid=nursery_uuid, owner_uuid=current_user.uuid, page=page, per_page=per_page, order=order,
        order_filed=order_filed, keyword=keyword, status=status, reference=reference, month=month, year=year,
        child_uuid=child_uuid
    )


@router.get("/dashboard/sales", response_model=list[schemas.NurserySale], status_code=201)
def get_sales(
        db: Session = Depends(get_db),
        month: Optional[int] = date.today().month,
        year: Optional[int] = date.today().year,
        current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    """
    Get nurseries sales
    """
    return crud.invoice.get_sales_by_nurseries_for_given_month_and_previous(db, current_user.uuid, month, year)


@router.get("/dashboard", response_model=schemas.DashboardInvoiceList)
def dashboard_get(
        nursery_uuid: str,
        month: int = Query(..., ge=1, le=12),
        year: int = Query(..., ge=2024),
        db: Session = Depends(get_db),
        page: int = 1,
        per_page: int = 30,
        order: str = Query("asc", enum=["asc", "desc"]),
        order_filed: str = "date_to",
        current_user: models.Owner = Depends(TokenRequired(roles=["owner"]))
):
    """
    get all with filters
    """
    res = crud.invoice.get_many(
        db=db, nursery_uuid=nursery_uuid, owner_uuid=current_user.uuid, page=page,
        per_page=per_page, order=order, order_filed=order_filed, month=month, year=year)

    # for r in res.data:
    #     print(f"{r.uuid} {r.total_hours} {r.total_overtime_hours}")
    return res


@router.get("/{uuid}", response_model=schemas.InvoiceDetails, status_code=200)
def get_details(
        uuid: str,
        db: Session = Depends(get_db),
        current_user=Depends(TokenRequired(roles=["owner"]))
):
    """
        Get quote details
    """
    invoice = crud.invoice.get_by_uuid(db, uuid)
    if not invoice:
        raise HTTPException(status_code=404, detail=__("invoice-not-found"))

    if current_user.role.code == "owner" and invoice.nursery.owner_uuid != current_user.uuid:
        raise HTTPException(status_code=404, detail=__("invoice-not-found"))

    # invoice.invoices_statistic = {
    #     st.value: crud.invoice.get_child_statistic(db, invoice.child_uuid, status=st) for st in models.InvoiceStatusType
    # }
    invoice.invoices_statistic = crud.invoice.get_child_statistic(db, invoice.child_uuid)

    return invoice


@router.post("/{uuid}/payments", response_model=schemas.Payment)
def create_payment(
        uuid: str,
        payment: schemas.PaymentCreate,
        db: Session = Depends(get_db),
        current_user=Depends(TokenRequired(roles=["owner"]))
):
    """
    Create payment
    """
    invoice = crud.invoice.get_by_uuid(db, uuid)
    if not invoice:
        raise HTTPException(status_code=404, detail=__("invoice-not-found"))
    if invoice.status == models.InvoiceStatusType.PAID:
        raise HTTPException(status_code=400, detail=__("invoice-already-paid"))
    if invoice.status == models.InvoiceStatusType.PROFORMA:
        raise HTTPException(status_code=400, detail=__("invoice-still-proforma"))

    if current_user.role.code == "owner" and invoice.nursery.owner_uuid != current_user.uuid:
        raise HTTPException(status_code=404, detail=__("invoice-not-found"))

    if payment.type == models.PaymentType.PARTIAL and payment.amount > invoice.amount_due:
        raise HTTPException(status_code=400, detail=__("payment-amount-exceeds"))

    return crud.invoice.create_payment(db, invoice, payment)


@router.put("/{uuid}/pending", response_model=schemas.InvoiceDetails)
def set_pending(
        uuid: str,
        db: Session = Depends(get_db),
        current_user=Depends(TokenRequired(roles=["owner"]))
):
    """
    Set invoice to pending
    """
    invoice = crud.invoice.get_by_uuid(db, uuid)
    if not invoice:
        raise HTTPException(status_code=404, detail=__("invoice-not-found"))

    if current_user.role.code == "owner" and invoice.nursery.owner_uuid != current_user.uuid:
        raise HTTPException(status_code=404, detail=__("invoice-not-found"))

    if invoice.status != models.InvoiceStatusType.PROFORMA:
        raise HTTPException(status_code=400, detail=__("invoice-not-proforma"))

    return crud.invoice.update_status(db, invoice, models.InvoiceStatusType.PENDING)


@router.put("/{uuid}/items", response_model=schemas.InvoiceDetails)
def update_items(
        uuid: str,
        items: schemas.InvoiceUpdate,
        db: Session = Depends(get_db),
        current_user=Depends(TokenRequired(roles=["owner"]))
):
    """
    Update/add invoice items
    """
    invoice = crud.invoice.get_by_uuid(db, uuid)
    if not invoice:
        raise HTTPException(status_code=404, detail=__("invoice-not-found"))

    if current_user.role.code == "owner" and invoice.nursery.owner_uuid != current_user.uuid:
        raise HTTPException(status_code=404, detail=__("invoice-not-found"))

    if invoice.status != models.InvoiceStatusType.PROFORMA:
        raise HTTPException(status_code=400, detail=__("invoice-not-proforma"))

    crud.invoice.add_update_items(db, invoice, items)
    return crud.invoice.get_by_uuid(db, uuid)


@router.post("/", response_model=schemas.InvoiceDetails)
def create(
        obj_in: schemas.InvoiceCreate,
        db: Session = Depends(get_db),
        current_user=Depends(TokenRequired(roles=["owner"]))
):
    """
    Add invoice
    """
    invoice = crud.invoice.get_by_uuid(db, obj_in.invoice_uuid)
    if not invoice:
        raise HTTPException(status_code=404, detail=__("invoice-not-found"))

    if current_user.role.code == "owner" and invoice.nursery.owner_uuid != current_user.uuid:
        raise HTTPException(status_code=404, detail=__("invoice-not-found"))

    if invoice.status != models.InvoiceStatusType.PROFORMA:
        raise HTTPException(status_code=400, detail=__("invoice-not-proforma"))

    return crud.invoice.create(db, invoice, obj_in)

