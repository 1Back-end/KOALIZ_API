import math

from typing import Optional
from sqlalchemy import or_
from sqlalchemy.orm import Session, aliased

from app.main import crud, schemas, models
from app.main.crud.base import CRUDBase


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
            TagAlias = aliased(models.Tags)
            TagElementAlias = aliased(models.TagElement)
            record_query = record_query.join(
                TagElementAlias, models.Quote.preregistration_uuid == TagElementAlias.element_uuid
            ).join(
                TagAlias, TagElementAlias.tag_uuid == TagAlias.uuid
            ).filter(
                TagAlias.type == models.TagTypeEnum.PRE_ENROLLMENT,
                TagAlias.uuid == tag_uuid,
            )

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


    @classmethod
    def update_settings(cls, db: Session, quote_obj: models.Quote, obj_in: schemas.QuoteSettingsUpdate) -> models.Quote:
        quote_obj.hourly_rate = obj_in.hourly_rate
        quote_obj.registration_fee = obj_in.registration_fee

        quote_obj.deposit_type = obj_in.deposit_type
        quote_obj.deposit_percentage = obj_in.deposit_percentage
        quote_obj.deposit_value = obj_in.deposit_value

        quote_obj.adaptation_type = obj_in.adaptation_type
        quote_obj.adaptation_hourly_rate = obj_in.adaptation_hourly_rate
        quote_obj.adaptation_hours_number = obj_in.adaptation_hours_number
        quote_obj.adaptation_package_costs = obj_in.adaptation_package_costs
        quote_obj.adaptation_package_days = obj_in.adaptation_package_days

        crud.preregistration.generate_quote(db, quote_obj.preregistration_uuid)

        db.commit()
        return quote_obj


    @classmethod
    def update_cmg(cls, db: Session, quote_obj: models.Quote, obj_in: schemas.CMGUpdate) -> models.Quote:

        quote_obj.cmg.family_type = obj_in.family_type
        quote_obj.cmg.number_children = obj_in.number_children
        quote_obj.cmg.annual_income = obj_in.annual_income

        crud.preregistration.determine_cmg(db=db, dependent_children=obj_in.number_children,
                                           family_type=obj_in.family_type, annual_income=obj_in.annual_income,
                                           birthdate=quote_obj.child.birthdate, quote_uuid=quote_obj.uuid)

        db.commit()
        return quote_obj


quote = CRUDQuote(models.Quote)


