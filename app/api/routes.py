from fastapi import APIRouter

from app.api.feedback import router as feedback_router
from app.api.models import router as models_router
from app.api.experiments import router as experiments_router

router = APIRouter()

@router.get("/")
async def root():
    return {
        "status": "ok"
    }

@router.get("/health")
async def health():
    return {
        "status": "healthy"
    }

router.include_router(feedback_router)
router.include_router(models_router)
router.include_router(experiments_router)
