from pydantic import BaseModel

class FeedbackCreate(BaseModel):
    solution_id: str
    feedback_text: str
