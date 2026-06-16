from fastapi import APIRouter

router = APIRouter(
    prefix="/models",
    tags=["models"]
)

@router.get("/current")
async def get_models():
    return {
        "version": 1,
        "criteria": []
    }