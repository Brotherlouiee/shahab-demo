"""Version-one API composition. Product routers are added only in their assigned stories."""

from fastapi import APIRouter

from .health import router as health_router
from .loans import router as loans_router
from .questionnaire import router as questionnaire_router
from .profiles import router as profiles_router
from .recommendations import router as recommendations_router

router = APIRouter()
router.include_router(health_router)
router.include_router(loans_router)
router.include_router(questionnaire_router)
router.include_router(profiles_router)
router.include_router(recommendations_router)
