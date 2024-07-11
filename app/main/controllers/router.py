from fastapi import APIRouter

from .authentication_controller import router as authentication
from .migration_controller import router as migration
from .utils_controller import router as utils

api_router = APIRouter()

api_router.include_router(authentication)
api_router.include_router(migration)
api_router.include_router(utils)
