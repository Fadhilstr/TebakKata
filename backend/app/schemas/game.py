from pydantic import BaseModel, Field
from datetime import date
import uuid


class TodayGameResponse(BaseModel):
    game_id: uuid.UUID
    game_date: date
    total_words: int = Field(description="Total vocabulary words in game index")

    class Config:
        from_attributes = True
