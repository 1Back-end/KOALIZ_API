import math
import uuid
from typing import Any, Optional
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.main.crud.base import CRUDBase
from app.main import schemas, models


class CRUDAuditLog(CRUDBase[models.AuditLog, schemas.AuditLogCreate, schemas.AuditLogUpdate]):

    @classmethod
    def create(self, db: Session, *, before_changes: Any, performed_by_uuid: Optional[str] = None, after_changes: Any, entity_type: str, entity_id: str, action: str) -> schemas.AuditLogSchema:
        try:
            audit_log = models.AuditLog(
                uuid=str(uuid.uuid4()),
                before_changes=before_changes,
                entity_type=entity_type,
                entity_id=entity_id,
                action=action,
                performed_by_uuid=performed_by_uuid,
                after_changes=after_changes
            )
            db.add(audit_log)
            db.commit()
            db.refresh(audit_log)
            return audit_log
        except Exception as e:
            print(str(e))
            db.rollback()

    @classmethod
    def get_auditlog_by_uuid(self, db: Session, uuid: str) -> schemas.AuditLogSchema:
        return db.query(models.AuditLog).filter(models.AuditLog.uuid == uuid).first()

    @classmethod
    def update(
        self, db: Session, *, db_obj: models.AuditLog, obj_in: schemas.AuditLogUpdate
    ) -> schemas.AuditLogSchema:
        try:
            update_data = obj_in.model_dump(exclude_unset=True)
            return super().update(db, db_obj=db_obj, obj_in=update_data)
        except Exception as e:
            print(str(e))
            db.rollback()

    @classmethod
    def get_multi(
        cls,
        db:Session,
        page:int = 1,
        per_page:int = 30,
        order:Optional[str] = 'desc',
        entity_id:Optional[str] = None,
        keyword:Optional[str]= None,
        order_filed:Optional[str] = "date_added"
    ):
        record_query = db.query(models.AuditLog)

        if entity_id:
            record_query = record_query.filter(models.AuditLog.entity_id==entity_id)

        if keyword:
            record_query = record_query.filter(
                or_(
                    models.AuditLog.entity_type.ilike('%' + str(keyword) + '%'),
                    models.AuditLog.entity_id.ilike('%' + str(keyword) + '%'),
                    models.AuditLog.action.ilike('%' + str(keyword) + '%'),
                )
            )

        if order and order.lower() == "asc":
            print(order)
            record_query = record_query.order_by(getattr(models.AuditLog, order_filed).asc())

        if order and order.lower() == "desc":
            print(order)
            print(order_filed)
            record_query = record_query.order_by(getattr(models.AuditLog, order_filed).desc())

        total = record_query.count()
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        return schemas.AuditLogList(
            total = total,
            pages = math.ceil(total/per_page),
            per_page = per_page,
            current_page =page,
            data =record_query
        )

audit_log = CRUDAuditLog(models.AuditLog)