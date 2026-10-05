from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
import time

from app.db.session import get_db
from app.services.game_service import GameService
from app.semantic.engine import semantic_engine
from app.core.timezone import get_now_jakarta
from app.core.logging import logger
from app.schemas.game import TodayGameResponse
from app.schemas.guess import GuessRequest, GuessResponse, GameHistoryResponse

router = APIRouter(prefix="/game", tags=["game"])

# Simple in-memory rate limiter per session_id (max 60 guesses per minute)
_RATE_LIMITS = {}


def check_rate_limit(session_id: str, limit: int = 60, window_seconds: int = 60):
    now = time.time()
    timestamps = _RATE_LIMITS.get(session_id, [])
    # Filter out timestamps older than window
    timestamps = [t for t in timestamps if now - t < window_seconds]
    if len(timestamps) >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Terlalu banyak tebakan dalam waktu singkat. Harap tunggu sebentar."
        )
    timestamps.append(now)
    _RATE_LIMITS[session_id] = timestamps


@router.get("/today", response_model=TodayGameResponse)
def get_today_game(db: Session = Depends(get_db)):
    """
    Returns today's game ID and date in Asia/Jakarta timezone.
    Secret word is never exposed in this endpoint.
    """
    game = GameService.get_or_create_daily_game(db)
    return TodayGameResponse(
        game_id=game.id,
        game_date=game.game_date,
        total_words=len(semantic_engine.words) if semantic_engine.words else 15000
    )


@router.get("/random", response_model=TodayGameResponse)
def get_random_game(db: Session = Depends(get_db)):
    """
    Returns a random practice game with a new secret word for unlimited play.
    """
    import random
    from datetime import timedelta
    from app.models.word import Word
    from app.models.daily_game import DailyGame
    from app.core.timezone import get_today_jakarta

    today_date = get_today_jakarta()
    today_game = db.query(DailyGame).filter(DailyGame.game_date == today_date).first()
    today_secret_id = today_game.secret_word_id if today_game else None

    # Exclude today's secret word so it is always a fresh different puzzle!
    query = db.query(Word).filter(Word.is_secret_eligible == True)
    if today_secret_id:
        query = query.filter(Word.id != today_secret_id)

    eligible_words = query.all()
    if not eligible_words:
        eligible_words = db.query(Word).limit(100).all()

    if not eligible_words:
        raise HTTPException(status_code=500, detail="Tidak ada kata rahasia tersedia.")

    chosen = random.choice(eligible_words)

    # Find a unique unused game_date
    for _ in range(100):
        random_fake_date = today_date - timedelta(days=random.randint(100, 50000))
        if not db.query(DailyGame).filter(DailyGame.game_date == random_fake_date).first():
            break
    else:
        random_fake_date = today_date - timedelta(days=random.randint(50001, 99999))

    game = DailyGame(game_date=random_fake_date, secret_word_id=chosen.id)
    db.add(game)
    db.commit()
    db.refresh(game)

    semantic_engine.get_or_create_daily_rank_map(chosen.normalized_word)
    return TodayGameResponse(
        game_id=game.id,
        game_date=game.game_date,
        total_words=len(semantic_engine.words) if semantic_engine.words else 15000
    )


@router.post("/guess", response_model=GuessResponse)
def submit_guess(req: GuessRequest, db: Session = Depends(get_db)):
    """
    Submits a player guess word for evaluation against the secret word.
    """
    check_rate_limit(req.session_id)

    start_time = time.time()
    response, error = GameService.submit_guess(
        db=db,
        game_id=req.game_id,
        raw_word=req.word,
        session_id=req.session_id
    )

    duration_ms = (time.time() - start_time) * 1000
    if error:
        logger.warning("Guess failed: '%s' - %s (%.2f ms)", req.word, error, duration_ms)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "kamus" in error else status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    logger.info(
        "Guess evaluated: '%s' -> Rank #%d (Sim: %.4f, Solved: %s) in %.2f ms",
        response.word, response.ranking, response.similarity, response.is_correct, duration_ms
    )
    return response


@router.get("/history", response_model=GameHistoryResponse)
def get_game_history(
    game_id: UUID = Query(...),
    session_id: str = Query(..., min_length=1, max_length=64),
    db: Session = Depends(get_db)
):
    """
    Retrieves the guess history for a given game and session.
    Reveals the secret word only if the player has solved the puzzle.
    """
    try:
        return GameService.get_history(db, game_id, session_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "timestamp_jakarta": get_now_jakarta().isoformat(),
        "vocab_size": len(semantic_engine.words),
        "embeddings_loaded": semantic_engine.embeddings is not None
    }
