from fastapi import APIRouter

router = APIRouter(
    prefix="/models",
    tags=["models"]
)

@router.get("/")
async def get_models():
    return []