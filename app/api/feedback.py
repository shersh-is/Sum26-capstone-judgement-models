from fastapi import APIRouter
from app.schemas.feedback import FeedbackCreate

router = APIRouter(
    prefix="/feedback",
    tags=["feedback"]
)

@router.post("/")
async def create_feedback(payload: FeedbackCreate):
    return {
        "accepted": True,
        "solution_id": payload.solution_id,
        "feedback_text": payload.feedback_text
    }