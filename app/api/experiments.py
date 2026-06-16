from fastapi import APIRouter
from app.schemas.experiment import ExpRunRequest

router = APIRouter(
    prefix="/experiments",
    tags=["experiments"]
)

@router.post("/run")
async def run_experiment(payload: ExpRunRequest):
    return {
        "run_id": "exp_001",
        "status": "running",
        "architecture": payload.architecture,
        "llm": payload.llm
    }
