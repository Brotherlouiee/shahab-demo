"""Version-one API composition. Product routers are added only in their assigned stories."""

from fastapi import APIRouter

from .health import router as health_router

router = APIRouter()
router.include_router(health_router)
