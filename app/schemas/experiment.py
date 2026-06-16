from pydantic import BaseModel

class ExpRunRequest(BaseModel):
    architecture: str
    llm: str
