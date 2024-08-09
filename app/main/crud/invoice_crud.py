import math
from uuid import uuid4

from fastapi import HTTPException
from typing import Optional, Union
from sqlalchemy import or_
from sqlalchemy.orm import Session, aliased, joinedload

from app.main import crud, schemas, models
from app.main.core.i18n import __
from app.main.crud.base import CRUDBase


class CRUDInvoice(CRUDBase[models.Invoice, None, None]):

    @classmethod
    def get_by_uuid(cls, db: Session, uuid: str) -> Optional[models.Invoice]:
        return db.query(models.Invoice).filter(models.Invoice.uuid == uuid).first()

    @classmethod
    def get_by_quote_uuid(cls, db: Session, quote_uuid: str) -> Union[list[models.Invoice], list]:
        return db.query(models.Invoice).filter(models.Invoice.quote_uuid == quote_uuid).all()

    @classmethod
    def delete_by_quote_uuid(cls, db: Session, quote_uuid: str) -> None:
        return db.query(models.Invoice).filter(models.Invoice.quote_uuid == quote_uuid).delete()

    @classmethod
    def update_status(cls, db: Session, invoice_obj: models.Invoice, status: models.InvoiceStatusType) -> models.Invoice:
        invoice_obj.status = status
        db.commit()
        return invoice_obj


    def get_many(
            self,
            db: Session,
            nursery_uuid: str,
            owner_uuid: str,
            page: int = 1,
            per_page: int = 30,
            order: Optional[str] = None,
            order_filed: Optional[str] = None,
            keyword: Optional[str] = None,
            status: Optional[str] = None,
            reference: str = None
    ):
        record_query = db.query(models.Invoice).filter(models.Invoice.nursery_uuid==nursery_uuid).filter(models.Invoice.nursery.has(models.Nursery.owner_uuid==owner_uuid))
        if status:
            record_query = record_query.filter(models.Invoice.status == status)

        if reference:
            record_query = record_query.filter(models.Invoice.reference == reference)

        if keyword:
            record_query = record_query.filter(models.Invoice.child.has(
                or_(
                    models.Child.firstname.ilike('%' + str(keyword) + '%'),
                    models.Child.lastname.ilike('%' + str(keyword) + '%'),
                ))
            )

        if order == "asc":
            record_query = record_query.order_by(getattr(models.Invoice, order_filed).asc())
        else:
            record_query = record_query.order_by(getattr(models.Invoice, order_filed).desc())

        total = record_query.count()
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        return schemas.InvoiceList(
            total=total,
            pages=math.ceil(total / per_page),
            per_page=per_page,
            current_page=page,
            data=record_query
        )


    @classmethod
    def update_cmg(cls, db: Session, invoice_obj: models.Invoice, obj_in: schemas.CMGUpdate) -> models.Invoice:

        invoice_obj.cmg.family_type = obj_in.family_type
        invoice_obj.cmg.number_children = obj_in.number_children
        invoice_obj.cmg.annual_income = obj_in.annual_income

        crud.preregistration.determine_cmg(db=db, dependent_children=obj_in.number_children,
                                           family_type=obj_in.family_type, annual_income=obj_in.annual_income,
                                           birthdate=invoice_obj.child.birthdate, invoice_uuid=invoice_obj.uuid)

        db.commit()
        return invoice_obj


    def generate_invoice(self, db: Session, quote_uuid: str, contract_uuid: str = None) -> None:
        quote = crud.quote.get_by_uuid(db, quote_uuid)
        if not quote:
            raise HTTPException(status_code=404, detail=__("quote-not-found"))

        self.delete_by_quote_uuid(db, quote_uuid)
        for quote_timetable in quote.timetables:
            new_invoice = models.Invoice(
                uuid=str(uuid4()),
                date_to=quote_timetable.date_to,
                invoicing_period_start=quote_timetable.invoicing_period_start,
                invoicing_period_end=quote_timetable.invoicing_period_end,
                amount=quote_timetable.amount,
                amount_paid=0,
                amount_due=quote_timetable.amount,
                status=models.InvoiceStatusType.PROFORMA,
                child_uuid=quote.child_uuid,
                quote_uuid=quote_uuid,
                nursery_uuid=quote.nursery_uuid,
                parent_guest_uuid=quote.parent_guest_uuid,
                contract_uuid=contract_uuid
            )
            db.add(new_invoice)
            for quote_item in quote_timetable.items:
                timetable_item = models.InvoiceItem(
                    uuid=str(uuid4()),
                    invoice_uuid=new_invoice.uuid,
                    title_fr=quote_item.title_fr,
                    title_en=quote_item.title_en,
                    amount=quote_item.amount,
                    total_hours=quote_item.total_hours,
                    unit_price=quote_item.unit_price
                )
                db.add(timetable_item)
        db.commit()


invoice = CRUDInvoice(models.Invoice)


