from fastapi import APIRouter

from .authentication_controller import router as authentication
from .migration_controller import router as migration

api_router = APIRouter()

api_router.include_router(authentication)
api_router.include_router(migration)