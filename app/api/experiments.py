from fastapi import APIRouter

router = APIRouter(
    prefix="/experiments",
    tags=["experiments"]
)

@router.post("/run")
async def run_experiment():
    return {
        "status": "started"
    }