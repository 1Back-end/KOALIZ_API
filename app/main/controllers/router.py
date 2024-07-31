from fastapi import APIRouter

from .administrator_controller import router as administrator
from .authentication_controller import router as authentication
from .helper_controller import router as helper
from .migration_controller import router as migration
from .nursery_controller import router as nursery
from .owner_controller import router as owner
from .preregistration_controller import router as preregistration
from .storage_controller import router as storage
from .membership_controller import router as membership
from .tag_controller import router as tag
from .audit_log_controller import router as audit_logs
from .notification_controller import router as notification
from .parent_controller import router as parent
from .device_controller import router as device
from .team_controller import router as team
from .employe_controller import router as employee
# from .message_controller import router as message

api_router = APIRouter()

api_router.include_router(audit_logs)
api_router.include_router(device)
api_router.include_router(authentication)
api_router.include_router(administrator)
api_router.include_router(owner)
api_router.include_router(membership)
api_router.include_router(nursery)
api_router.include_router(parent)
# api_router.include_router(message)
api_router.include_router(preregistration)
api_router.include_router(notification)
api_router.include_router(migration)
api_router.include_router(storage)
api_router.include_router(tag)
api_router.include_router(helper)
api_router.include_router(team)
api_router.include_router(employee)

