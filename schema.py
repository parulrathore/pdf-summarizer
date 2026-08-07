from pydantic import BaseModel, Field
from typing import Literal, Optional

class KeyPoint(BaseModel):
    point: str
    page_ref: Optional[int] = None

class Entities(BaseModel):
    people: list[str] = []
    organizations: list[str] = []
    dates: list[str] = []

class DocumentSummary(BaseModel):
    title: str
    document_type: Literal["report", "profile", "article", "financial", "other"]
    summary: str = Field(description="2-4 sentence overview")
    key_points: list[KeyPoint]
    entities: Entities
    confidence: Literal["high", "medium", "low"]