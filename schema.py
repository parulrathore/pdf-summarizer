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

class EmailSummary(BaseModel):
    subject: str
    sender: str
    summary: str = Field(description="2-4 sentence overview")
    key_points: list[str]
    action_items: list[str] = []
    requires_response: bool
    sentiment: Literal["neutral", "urgent", "positive", "negative"]
    confidence: Literal["high", "medium", "low"]