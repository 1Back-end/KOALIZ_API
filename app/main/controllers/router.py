from fastapi import APIRouter

from .administrator_controller import router as administrator
from .authentication_controller import router as authentication
from .migration_controller import router as migration
from .nursery_controller import router as nursery
from .owner_controller import router as owner
from .preregistration_controller import router as preregistration
from .storage_controller import router as storage
from .membership_controller import router as membership

api_router = APIRouter()

api_router.include_router(authentication)
api_router.include_router(administrator)
api_router.include_router(owner)
api_router.include_router(membership)
api_router.include_router(nursery)
api_router.include_router(preregistration)
api_router.include_router(migration)
api_router.include_router(storage)
