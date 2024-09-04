import uuid
from sqlalchemy.orm import Session
from typing import Any, List, Union
from fastapi import APIRouter, Body, Depends, HTTPException

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


@router.post("/settings", response_model=List[schemas.NotificationSettingUserSchema])
def notification_setting(    
    *,
    db: Session = Depends(dependencies.get_db),
    obj_in: List[schemas.SettingConfig] = Body(...),
    current_user: models.Administrator = Depends(dependencies.TokenRequired(roles=[]))
) -> Any:

    """
        Update my notification settings
    """
    
    notifs_not_founds = []
    notifs = []

    for item in obj_in:
        notification = item.model_dump(exclude_unset=True)
        setting = db.query(models.NotificationSetting).\
            filter_by(key=notification["key"]).\
            filter(models.NotificationSetting.role_uuid==current_user.role_uuid).first()
        if not setting:
            notifs_not_founds.append(notification["key"])

    if len(notifs_not_founds):
        str2 = " - ".join(notifs_not_founds)
        raise HTTPException(
            status_code=404,
            detail=__("setting-not-exist")+" : "+str2,
        )

    for item in obj_in:
        notification = item.model_dump(exclude_unset=True)
        setting = db.query(models.NotificationSetting).\
            filter_by(key=notification["key"]).\
            filter(models.NotificationSetting.role_uuid==current_user.role_uuid).\
            first()

        notif_setting = db.query(models.NotificationSettingUser).filter_by(user_public_id=current_user.uuid, notification_setting_uuid=setting.uuid).first()
        if notif_setting:
            notif_setting.push_actived = notification["push_actived"] if "push_actived" in notification else notif_setting.push_actived
            notif_setting.mail_actived = notification["mail_actived"] if "mail_actived" in notification else notif_setting.mail_actived
            notif_setting.in_app_actived = notification["in_app_actived"] if "in_app_actived" in notification else notif_setting.in_app_actived
            db.commit()
        else:
            notif_setting = models.NotificationSettingUser(
                uuid=str(uuid.uuid4()),
                user_uuid=current_user.uuid,
                notification_setting_uuid=setting.uuid,
                push_actived=notification["push_actived"] if "push_actived" in notification else False,
                mail_actived=notification["mail_actived"] if "mail_actived" in notification else False,
                in_app_actived=notification["in_app_actived"] if "in_app_actived" in notification else False
            )
            db.add(notif_setting)
            db.commit()
        
        notifs.append(notif_setting)

    return notifs


@router.get("/settings", response_model=List[schemas.NotificationSettingUserSchema])
def get_notification_setting(    
    *,
    db: Session = Depends(dependencies.get_db),
    current_user: models.Administrator = Depends(dependencies.TokenRequired(roles=None))
) -> Any:

    """
        List my notification settings
    """

    return db.query(models.NotificationSettingUser).filter_by(user_uuid=current_user.uuid).\
        filter(models.NotificationSettingUser.notification_setting.has(role_uuid=current_user.role_uuid)).\
            order_by(models.NotificationSettingUser.date_added.asc()).\
        all()
