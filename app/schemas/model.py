from pydantic import BaseModel

class Criterion(BaseModel):
    id: str
    description: str

class JudgementModel(BaseModel):
    version: int
    criteria: list[Criterion]
