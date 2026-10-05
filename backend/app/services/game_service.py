import hashlib
from typing import Optional, Tuple
from datetime import date
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.timezone import get_today_jakarta
from app.core.logging import logger
from app.models.word import Word
from app.models.daily_game import DailyGame
from app.models.guess import Guess
from app.semantic.normalizer import normalize_word
from app.semantic.engine import semantic_engine
from app.schemas.guess import GuessResponse, GameHistoryResponse, GuessHistoryItem


class GameService:
    @staticmethod
    def get_or_create_daily_game(db: Session, target_date: Optional[date] = None) -> DailyGame:
        if target_date is None:
            target_date = get_today_jakarta()

        game = db.query(DailyGame).filter(DailyGame.game_date == target_date).first()
        if game:
            # Pre-warm semantic engine rank map
            secret_norm = game.secret_word.normalized_word
            semantic_engine.get_or_create_daily_rank_map(secret_norm)
            return game

        logger.info("Creating new DailyGame for date %s (Asia/Jakarta)...", target_date)
        
        # Select deterministic secret word based on date hash
        eligible_words = db.query(Word).filter(Word.is_secret_eligible == True).order_by(Word.id).all()
        if not eligible_words:
            # Fallback to any word if secret eligible not yet flagged
            eligible_words = db.query(Word).order_by(Word.id).limit(1000).all()

        if not eligible_words:
            raise RuntimeError("Cannot create daily game: No words available in database.")

        date_str = target_date.isoformat()
        hash_val = int(hashlib.sha256(date_str.encode()).hexdigest(), 16)
        chosen_idx = hash_val % len(eligible_words)
        secret_word = eligible_words[chosen_idx]

        game = DailyGame(
            game_date=target_date,
            secret_word_id=secret_word.id
        )
        db.add(game)
        db.commit()
        db.refresh(game)

        # Pre-warm semantic engine cache
        semantic_engine.get_or_create_daily_rank_map(secret_word.normalized_word)
        logger.info("DailyGame created for %s with secret word ID %d", target_date, secret_word.id)
        return game

    @staticmethod
    def submit_guess(
        db: Session,
        game_id: UUID,
        raw_word: str,
        session_id: str
    ) -> Tuple[Optional[GuessResponse], Optional[str]]:
        """
        Processes a guess. Returns (GuessResponse, None) on success,
        or (None, error_message) on validation/not-found failure.
        """
        normalized = normalize_word(raw_word)
        if not normalized:
            return None, "Kata tidak valid. Gunakan huruf alfabet bahasa Indonesia."

        game = db.query(DailyGame).filter(DailyGame.id == game_id).first()
        if not game:
            return None, "Game harian tidak ditemukan."

        secret_word_obj = game.secret_word
        secret_norm = secret_word_obj.normalized_word

        # Evaluate similarity & rank via semantic engine
        eval_result = semantic_engine.evaluate_guess(secret_norm, normalized)
        if eval_result is None:
            return None, f"Kata '{normalized}' tidak ditemukan dalam kamus permainan."

        ranking, similarity = eval_result
        is_correct = (ranking == 1 or normalized == secret_norm)

        # Find or create Word object for the guess
        guessed_word_obj = db.query(Word).filter(Word.normalized_word == normalized).first()
        if not guessed_word_obj:
            guessed_word_obj = Word(
                word=normalized,
                normalized_word=normalized,
                category="general",
                frequency=1,
                is_secret_eligible=False
            )
            db.add(guessed_word_obj)
            db.flush()

        # Save guess to DB
        guess_record = Guess(
            game_id=game.id,
            session_id=session_id,
            word_id=guessed_word_obj.id,
            similarity_score=similarity,
            ranking=ranking
        )
        db.add(guess_record)
        db.commit()

        # Total guesses count for this player in this game
        guess_count = db.query(func.count(Guess.id)).filter(
            Guess.game_id == game.id,
            Guess.session_id == session_id
        ).scalar()

        response = GuessResponse(
            word=normalized,
            ranking=ranking,
            similarity=similarity,
            is_correct=is_correct,
            guess_count=guess_count,
            secret_word=secret_norm if is_correct else None
        )
        return response, None

    @staticmethod
    def get_history(db: Session, game_id: UUID, session_id: str) -> GameHistoryResponse:
        game = db.query(DailyGame).filter(DailyGame.id == game_id).first()
        if not game:
            raise ValueError("Game tidak ditemukan.")

        guesses = db.query(Guess).filter(
            Guess.game_id == game_id,
            Guess.session_id == session_id
        ).order_by(Guess.created_at.desc()).all()

        history_items = [
            GuessHistoryItem(
                word=g.word.normalized_word,
                ranking=g.ranking,
                similarity=g.similarity_score,
                created_at=g.created_at
            )
            for g in guesses
        ]

        is_solved = any(g.ranking == 1 for g in guesses)
        best_rank = min((g.ranking for g in guesses), default=None)

        return GameHistoryResponse(
            game_id=game_id,
            session_id=session_id,
            total_guesses=len(guesses),
            is_solved=is_solved,
            best_ranking=best_rank,
            secret_word=game.secret_word.normalized_word if is_solved else None,
            guesses=history_items
        )
