from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="Judgement Model API"
)

app.include_router(router)