import logging

from app.main.crud.notification_crud import notification
from app.main.models.db.session import SessionLocal
from app.main.utils.one_signal import onesignal_notification


logger = logging.getLogger(__name__)


class NotificationConsume:

    @staticmethod
    def consume_general(message) -> bool:
        print("In General")
        try:
            db = SessionLocal()

            if not message["payload"]:
                return False

            notification.create(db=db, obj_in=message["payload"]["obj_in"])

            include_player_ids = []
            # include_player_ids = auth.get_user_devices(user_uuid=message["payload"]["channel"])
            print(f"+++++++++++++++++ Player ids {include_player_ids}")
            if include_player_ids:
                print("==================== onesignal res")
                res = onesignal_notification(payload=message["payload"]["onesignal_dict"], include_player_ids=include_player_ids)
                print(res)
                print("==================== onesignal res")

            db.close()
            return True
        except Exception as e:
            logger.critical(f'Error consuming {message["payload"]["obj_in"]["type"]} {e}')
            return False
