from fastapi import APIRouter

router = APIRouter(
    prefix="/feedback",
    tags=["feedback"]
)

@router.post("/")
async def create_feedback():
    return {
        "message": "feedback endpoint"
    }