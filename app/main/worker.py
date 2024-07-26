import os
import time
from celery.schedules import crontab

from celery import Celery

from app.main.core.config import Config


celery = Celery(__name__)
celery.conf.timezone = 'Europe/Berlin'
celery.conf.broker_url = Config.CELERY_BROKER_URL
celery.conf.result_backend = Config.CELERY_RESULT_BACKEND


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    pass

# celery.conf.beat_schedule = {
    # 'every-1h30-pm-update-users-grade': {
    #     'task': 'update_users_grade',
    #     # 'schedule': crontab(hour=13, minute=30)
    #     'schedule': crontab(minute="*/15")
    # },
    # 'every-first-day-month-save-number-of-user-and-order': {
    #     'task': 'save_number_of_user_and_order',
    #     'schedule': crontab(hour=5, minute=00)
    # },
    # 'activate-ambassador-account-on-third-command': {
    #     'task': 'activate_ambassador_account_on_third_command',
    #     'schedule': crontab(hour=13, minute=00)
    # },
    # 'add-every-day-1': {
    #     'task': 'reminder_program',
    #     'schedule': crontab(minute=1),
    # },
# }

@celery.task(name="create_task")
def create_task(task_type):
    time.sleep(int(task_type) * 10)
    print(f"Task {task_type} done")
    return True