from fastapi import APIRouter

from .administrator_controller import router as administrator
from .authentication_controller import router as authentication
from .helper_controller import router as helper
from .invoice_controller import router as invoice
from .migration_controller import router as migration
from .nursery_controller import router as nursery
from .owner_controller import router as owner
from .preregistration_controller import router as preregistration
from .quote_controller import router as quote
from .storage_controller import router as storage
from .membership_controller import router as membership
from .tag_controller import router as tag
from .audit_log_controller import router as audit_logs
from .notification_controller import router as notification
from .nursery_close_hours_controller import router as nursery_close_hours
from .parent_controller import router as parent
from .team_device_controller import router as team_device
from .team_controller import router as team
from .employe_controller import router as employee
from .message_controller import router as message
from .nap_controller import router as nap
from .health_record_controller import router as health_record
from .hygiene_change_controller import router as hygiene_change
from .nursery_holidays_controller import router as nursery_holidays
from .observation_controller import router as observation
from .meal_controller import router as meal_controller
from .child_activity_controller import router as child_activity
from .media_controller import router as media
from .occasional_presence_controller import router as occasional_presence
from .absence_controller import router as absence
from .attendance_controller import router as attendance
from .activity_category_controller import router as activity_category
from .activity_controller import router as activity_controller
from .contract_controller import router as contract
from .invoicing_settings_controller import router as invoicing_settings
from .copy_parameters_controller import router as copy_parameters_controller
from .send_mail_controller import router as send_mail_controller
from .job_controller import router as job
from .group_controller import router as group
from .employee_planning_controller import router as employee_planning

api_router = APIRouter()

api_router.include_router(send_mail_controller)
api_router.include_router(audit_logs)
api_router.include_router(team_device)
api_router.include_router(authentication)
api_router.include_router(administrator)
api_router.include_router(owner)
api_router.include_router(contract)
api_router.include_router(membership)
api_router.include_router(nursery)
api_router.include_router(parent)
api_router.include_router(health_record)
api_router.include_router(hygiene_change)
api_router.include_router(nap)
api_router.include_router(child_activity)
api_router.include_router(media)
api_router.include_router(observation)
api_router.include_router(attendance)
api_router.include_router(absence)
api_router.include_router(occasional_presence)
api_router.include_router(message)
api_router.include_router(preregistration)
api_router.include_router(quote)
api_router.include_router(invoice)
api_router.include_router(invoicing_settings)
api_router.include_router(notification)
api_router.include_router(migration)
api_router.include_router(storage)
api_router.include_router(tag)
api_router.include_router(helper)
api_router.include_router(nursery_close_hours)
api_router.include_router(nursery_holidays)
api_router.include_router(meal_controller)
api_router.include_router(employee)
api_router.include_router(team)
api_router.include_router(activity_controller)
api_router.include_router(activity_category)
api_router.include_router(copy_parameters_controller)
api_router.include_router(job)
api_router.include_router(group)
api_router.include_router(employee_planning)
