from datetime import datetime, timedelta
import math
from typing import Union, Optional, List

from fastapi import HTTPException
from pydantic import EmailStr
from sqlalchemy import or_

from app.main.core.i18n import __
from app.main.crud.base import CRUDBase
from sqlalchemy.orm import Session,joinedload
from app.main import crud, schemas, models
import uuid
from app.main.core.security import get_password_hash, verify_password, generate_code, generate_slug


class CRUDQuote(CRUDBase[models.Quote, None, None]):

    @classmethod
    def get_by_uuid(cls, db: Session, uuid: str) -> Optional[models.Quote]:
        return db.query(models.Quote).filter(models.Quote.uuid == uuid).first()


    @classmethod
    def update_status(cls, db: Session, quote_obj: models.Quote, status: models.QuoteStatusType) -> models.Quote:
        quote_obj.status = status
        db.commit()
        return quote_obj

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
            tag_uuid: str = None
    ):
        record_query = db.query(models.Quote).filter(models.Quote.nursery_uuid==nursery_uuid).filter(models.Quote.nursery.has(models.Nursery.owner_uuid==owner_uuid))
        if status:
            record_query = record_query.filter(models.Quote.status == status)

        if keyword:
            record_query = record_query.filter(models.Quote.child.has(
                or_(
                    models.Child.firstname.ilike('%' + str(keyword) + '%'),
                    models.Child.lastname.ilike('%' + str(keyword) + '%'),
                ))
            )

        if tag_uuid:
            elements = self.get_elements_by_tag(db, tag_uuid)
            element_uuids = [element.get("data", {}).uuid for element in elements]
            record_query = record_query.filter(models.PreRegistration.uuid.in_(element_uuids))

        if order == "asc":
            record_query = record_query.order_by(getattr(models.Quote, order_filed).asc())
        else:
            record_query = record_query.order_by(getattr(models.Quote, order_filed).desc())

        total = record_query.count()
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        return schemas.QuoteList(
            total=total,
            pages=math.ceil(total / per_page),
            per_page=per_page,
            current_page=page,
            data=record_query
        )


quote = CRUDQuote(models.Quote)


