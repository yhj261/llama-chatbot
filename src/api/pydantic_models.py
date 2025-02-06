from pydantic import BaseModel, Field


class QueryInput(BaseModel):
    query: str
    session_id: str = Field(default=None)
    model: str = Field(default="Llama-3.1-8B-Instruct")


class QueryResponse(BaseModel):
    answer: str
    session_id: str
    model: str
