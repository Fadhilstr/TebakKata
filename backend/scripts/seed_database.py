import os
import sys
import json
import numpy as np
from sqlalchemy import text

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import SessionLocal, engine, Base
from app.models.word import Word
from app.models.daily_game import DailyGame
from app.services.game_service import GameService
from app.core.timezone import get_today_jakarta
from app.core.logging import logger


def get_vocab_dir():
    candidates = [
        "/app/data/vocabulary",
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "vocabulary")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "vocabulary")),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return candidates[1]


def seed_database():
    vocab_dir = get_vocab_dir()
    vocab_json = os.path.join(vocab_dir, "game_vocabulary.json")
    emb_npy = os.path.join(vocab_dir, "embeddings.npy")

    assert os.path.exists(vocab_json), f"Vocabulary JSON not found at {vocab_json}"

    with open(vocab_json, "r", encoding="utf-8") as f:
        vocab = json.load(f)

    embeddings = None
    if os.path.exists(emb_npy):
        print(f"Loading precomputed embeddings from {emb_npy}...")
        embeddings = np.load(emb_npy)

    print("Connecting to database...")
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        word_count = db.query(Word).count()
        print(f"Current words in DB: {word_count}")

        if word_count < len(vocab):
            print(f"Seeding {len(vocab)} words into database...")
            batch = []
            for i, item in enumerate(vocab):
                norm = item["normalized_word"]
                emb_val = embeddings[i].tolist() if embeddings is not None and i < len(embeddings) else None

                word_obj = Word(
                    word=item["word"],
                    normalized_word=norm,
                    category=item.get("category", "general"),
                    frequency=item.get("frequency", 0),
                    is_secret_eligible=item.get("is_secret_eligible", False),
                    embedding=emb_val
                )
                batch.append(word_obj)

                if len(batch) >= 1000:
                    db.bulk_save_objects(batch)
                    db.commit()
                    batch = []
                    print(f"  Inserted {i + 1}/{len(vocab)} words...")

            if batch:
                db.bulk_save_objects(batch)
                db.commit()
            print("Words seeding complete!")

        # Initialize today's game
        today = get_today_jakarta()
        game = db.query(DailyGame).filter(DailyGame.game_date == today).first()
        if not game:
            game = GameService.get_or_create_daily_game(db, target_date=today)
            print(f"Initialized DailyGame for {today} (ID: {game.id})")
        else:
            print(f"DailyGame already exists for {today} (ID: {game.id})")

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
