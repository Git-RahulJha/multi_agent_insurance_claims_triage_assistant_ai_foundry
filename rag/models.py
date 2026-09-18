from pydantic import BaseModel


class RetrievedChunk(BaseModel):
    id: str
    title: str
    content: str
    category: str
    source: str
    chunk_id: str
    score: float