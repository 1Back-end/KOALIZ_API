from sqlalchemy.orm import Session
from typing import Any, Union
from fastapi import APIRouter, Depends

from app.main import models, schemas
from app.main.core import dependencies
from app.main.core.dependencies import TokenRequired, get_db
from app.main.core.i18n import __
from app.main.crud.notification_crud import notification


router = APIRouter(
    prefix="/notifications",
    tags=["notifications"]
)


@router.get("/all", response_model=schemas.NotificationList, status_code=200)
def get_all(
        page: int = 1,
        per_page: int = 20,
        type: str = None,
        db: Session = Depends(get_db),
        current_user: models.Administrator = Depends(TokenRequired(roles =[]))
) -> Any:

    """ Get all user's notifications """

    notifications = notification.get_by_user(db=db, page=page, per_page=per_page, type=type, user_uuid=current_user.uuid)

    db.close()
    return notifications


@router.delete("/many", response_model=schemas.Msg, status_code=200)
def delete_many(
        *,
        notification_uuids: list[str] = None,
        db: Session = Depends(dependencies.get_db),
        current_user: models.Administrator = Depends(TokenRequired(roles =[]))
) -> Any:

    """ Delete notifications """

    if not notification_uuids:
        notification.delete(db=db, user_uuid=current_user.uuid)
        notifications = []
    else:
        notification.delete(db=db, uuids=notification_uuids, user_uuid=current_user.uuid)
        notifications = notification.get_multi_by_user(db=db, user_uuid=current_user.uuid,
                                                            uuids=notification_uuids)
    total_unread = notification.unread_notification_count(db=db, user_uuid=current_user.uuid)

    db.close()
    return {"message": __("notifications-deleted-success")}


@router.put("/many", response_model=Union[schemas.Msg, list[schemas.Notification]], status_code=200)
def mark_as_read(
        *,
        notification_uuids: list[str] = None,
        db: Session = Depends(dependencies.get_db),
        current_user: models.Administrator = Depends(TokenRequired(roles =[]))

) -> Any:

    """ Mark notifications as read """

    if not notification_uuids:
        notification.read(db=db, user_uuid=current_user.uuid, uuids=[])
        notifications = []
    else:
        notification.read(db=db, uuids=notification_uuids, user_uuid=current_user.uuid)

        notifications = notification.get_multi_by_user(db=db, user_uuid=current_user.uuid,
                                                            uuids=notification_uuids)
    db.close()
    if not notification_uuids:
        return {"message": __("notifications-read-success")}
    else:
        return notifications


@router.get("/unread/count", response_model=int, status_code=200)
def get_total_unread(
        *,
        db: Session = Depends(dependencies.get_db),
        current_user: models.Administrator = Depends(TokenRequired(roles =[]))

) -> Any:

    """ Count unread notifications """

    notifications = notification.unread_notification_count(db=db, user_uuid=current_user.uuid)
    db.close()
    return notifications
