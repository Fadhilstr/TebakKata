from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid


class GuessRequest(BaseModel):
    game_id: uuid.UUID
    word: str = Field(..., min_length=2, max_length=50)
    session_id: str = Field(..., min_length=1, max_length=64)


class GuessResponse(BaseModel):
    word: str
    ranking: int
    similarity: float
    is_correct: bool
    guess_count: int
    secret_word: Optional[str] = None  # ONLY returned when is_correct is True


class GuessHistoryItem(BaseModel):
    word: str
    ranking: int
    similarity: float
    created_at: datetime

    class Config:
        from_attributes = True


class GameHistoryResponse(BaseModel):
    game_id: uuid.UUID
    session_id: str
    total_guesses: int
    is_solved: bool
    best_ranking: Optional[int] = None
    secret_word: Optional[str] = None  # ONLY returned if is_solved is True
    guesses: List[GuessHistoryItem]
