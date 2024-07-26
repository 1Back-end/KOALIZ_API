import math
from typing import Any, Dict, Union
from uuid import uuid4

from sqlalchemy.orm import Session

from app.main.crud.base import CRUDBase
from app.main.models import Notification
from app.main.schemas import NotificationCreate, NotificationUpdate, DataList


class CRUDNotification(CRUDBase[Notification, NotificationCreate, NotificationUpdate]):

    def create(self, db: Session, *, obj_in: NotificationCreate) -> Notification:

        if isinstance(obj_in, dict):
            obj_in = obj_in
        else:
            obj_in = obj_in.dict(exclude_unset=True)

        db_obj = Notification(
            uuid=str(uuid4()),
            type=obj_in['type'],
            user_uuid=obj_in['user_uuid'],
            payload_json=obj_in['payload_json']
        )

        db.add(db_obj)
        db.commit()

        return db_obj

    def update(
            self, db: Session, *, db_obj: Notification, obj_in: Union[NotificationUpdate, Dict[str, Any]]
    ) -> Notification:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def get_by_user(self, db: Session, *, page: int = 1, per_page: int = 100, user_uuid: str, type: str = None) -> DataList:

        record_query = db.query(Notification).filter_by(user_uuid=user_uuid).order_by(Notification.date_added.desc())

        if type:
            record_query = record_query.filter(Notification.type == type)

        total = record_query.count()

        result = record_query.offset((page - 1) * per_page).limit(per_page).all()

        return DataList(
            total=total,
            pages=math.ceil(total / per_page),
            current_page=page,
            per_page=per_page,
            data=result
        )

    def unread_notification_count(self, db: Session, *, user_uuid: str) -> int:
        return db.query(Notification).filter(Notification.is_read != True, Notification.user_uuid == user_uuid).count()


    def delete(self, db: Session, user_uuid: str, uuids: list[str] = None) -> DataList:

        notifications = db.query(Notification).filter_by(user_uuid=user_uuid)
        if uuids:
            notifications = notifications.filter(Notification.uuid.in_(uuids))
        notifications.delete(synchronize_session=False)
        db.commit()

    def read(self, db: Session, user_uuid: str, uuids: list[int]) -> DataList:

        notifications = db.query(Notification).filter_by(user_uuid=user_uuid).filter(
            Notification.is_read == False)
        
        if len(uuids):
            notifications = notifications.filter(Notification.uuid.in_(uuids))

        for notification in notifications.all():
            if notification.is_read == False:
                notification.is_read = True
                db.commit()

    def get_multi_by_user(self, db: Session, user_uuid: str, uuids: list[str]) -> list[Notification]:

        record_query = db.query(Notification).filter_by(user_uuid=user_uuid).order_by(Notification.date_added.desc())
        return record_query.filter(Notification.uuid.in_(uuids)).all()


notification = CRUDNotification(Notification)
