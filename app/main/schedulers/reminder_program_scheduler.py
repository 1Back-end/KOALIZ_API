from datetime import datetime
import uuid

from sqlalchemy import DateTime, cast, func, or_, text
from app.main import models
from app.main.models.db.session import SessionLocal
from app.main.utils import logger
from dateutil.relativedelta import relativedelta
from dateutil import parser

def reminder_program():
    try:
        logger.info("Reminder program begin")

        # db = SessionLocal()

        # today = datetime.now()

        # programs = db.query(models.TrackingCase).\
        #     filter(models.TrackingCase.interaction_type=="ACTIVITY_REMINDER").\
        #     filter(func.to_timestamp(models.TrackingCase.details['datetime'].astext, 'YYYY-MM-DD"T"HH24:MI:SS"Z"') >= today)
        #     # filter(cast(models.TrackingCase.details['datetime'], DateTime) >= today).\


        # for program in programs.all():

        #     folder: models.PreRegistration = db.query(models.PreRegistration).\
        #         filter(models.PreRegistration.uuid==program.preregistration_uuid).first()
        #     if folder:
        #         owner_uuid = folder.nursery.owner_uuid
        #         # nursery_name = folder.nursery.name

        #         # "datetime": "2024-07-25T18:38:07.809000Z",
        #         program_date = program.details["datetime"]
        #         program_title = program.details["title"]
        #         program_description = program.details["description"]
        #         activity_reminder_type_title = program.details["activity_reminder_type"]['title_fr']
        #         activity_reminder_type_title_en = program.details["activity_reminder_type"]['title_en']
        #         print("activity_reminder_type_title: ", activity_reminder_type_title)

        #         # Utilisation de dateutil
        #         date_time_obj2 = parser.isoparse(program_date)
        #         print("\nUtilisation de dateutil:")
        #         print("Date:", date_time_obj2.date())
        #         print("Heure:", date_time_obj2.time())

        #         diff = relativedelta(date_time_obj2.replace(tzinfo=None), today)
        #         time_minutes = diff.minutes
        #         print(f"time_minutes : {time_minutes}")
        #         headings = {
        #             "fr": activity_reminder_type_title +" : "+ program_title, 
        #             'en': activity_reminder_type_title_en +" : "+ program_title
        #         }
        #         contents = {"fr": program_description}
        #         payload_notification = {"body": contents, "title": headings}

        #         if time_minutes == 2 * 60:
        #             # message = f"Votre programme de la crêche {nursery_name} du {date_time_obj2.date()} à {date_time_obj2.time()} débute dans 2 heures."
        #             # Create the notification
        #             notification = models.Notification(
        #                 uuid=str(uuid.uuid4()),
        #                 type="EVENT_NEW_NOTIFICATION", 
        #                 payload_json=payload_notification, 
        #                 user_uuid=owner_uuid, 
        #             )
        #             db.add(notification)
        #             db.flush()

        #             print("notification_id: ", notification.uuid)
        #             db.commit()

        #             # include_player_ids = [device.player_id for device in db.query(models.Device).filter(models.Device.user_public_id == user.user_public_id).all()]
        #             # print("include_player_ids before: ", include_player_ids)
        #             # if include_player_ids:
        #             #     print("include_player_ids after: ",include_player_ids)
        #             #     one_signal_notification(
        #             #         contents=contents, 
        #             #         include_player_ids=include_player_ids, 
        #             #         web_url=web_url,
        #             #         headings=headings, 
        #             #         data={"type": "REMINDER_PROGRAM", "item": {"date_reminder": f"{program.date}"}}
        #             #     )

        #     if time_minutes == 0:

        #         # Create the notification
        #         notification = models.Notification(
        #             uuid=str(uuid.uuid4()),
        #             type="EVENT_NEW_NOTIFICATION", 
        #             payload_json=payload_notification, 
        #             user_uuid=owner_uuid, 
        #         )
        #         db.add(notification)
        #         db.flush()
        #         print("notification_id: ", notification.uuid)
        #         db.commit()

        #             # include_player_ids = [device.player_id for device in db.query(models.Device).filter(models.Device.user_public_id == user.user_public_id).all()]
        #             # print("include_player_ids before : ", include_player_ids)
        #             # if include_player_ids:
        #             #     print("include_player_ids after: ", include_player_ids)
        #             #     one_signal_notification(
        #             #         contents=contents, 
        #             #         include_player_ids=include_player_ids, 
        #             #         web_url=web_url,
        #             #         headings=headings, 
        #             #         data={"type": "REMINDER_PROGRAM", "item": {"date_reminder": f"{program.date}"}}
            
        #         #     )

        logger.info("Finish program")

        # db.close()
        return "success"
    except Exception as e:
        print(str(e))
        pass