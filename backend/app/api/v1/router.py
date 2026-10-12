"""Version-one API composition. Product routers are added only in their assigned stories."""

from fastapi import APIRouter

from .account_access import router as account_access_router
from .bookmarks import router as bookmarks_router
from .health import router as health_router
from .loans import router as loans_router
from .profiles import router as profiles_router
from .questionnaire import router as questionnaire_router
from .recommendation_history import router as recommendation_history_router
from .recommendations import router as recommendations_router

router = APIRouter()
router.include_router(account_access_router)
router.include_router(health_router)
router.include_router(loans_router)
router.include_router(questionnaire_router)
router.include_router(profiles_router)
router.include_router(recommendations_router)
router.include_router(recommendation_history_router)

router.include_router(bookmarks_router)
