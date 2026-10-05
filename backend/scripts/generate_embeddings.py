import os
import sys
import json
import argparse
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings
from app.core.logging import logger


def generate_and_save_embeddings(to_db: bool = False):
    candidates = [
        "/app/data/vocabulary",
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "vocabulary")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "vocabulary")),
    ]
    vocab_dir = candidates[1]
    for c in candidates:
        if os.path.exists(os.path.join(c, "game_vocabulary.json")):
            vocab_dir = c
            break

    vocab_path = os.path.join(vocab_dir, "game_vocabulary.json")
    out_npy_path = os.path.join(vocab_dir, "embeddings.npy")
    out_index_path = os.path.join(vocab_dir, "vocab_index.json")

    assert os.path.exists(vocab_path), f"File {vocab_path} not found"

    with open(vocab_path, "r", encoding="utf-8") as f:
        vocab = json.load(f)

    words = [item["normalized_word"] for item in vocab]
    print(f"Loaded {len(words)} words from {vocab_path}")

    print(f"Loading SentenceTransformer: {settings.EMBEDDING_MODEL_NAME}...")
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)

    print("Generating normalized contextual embeddings for Indonesian...")
    framed_words = [f"kata bahasa Indonesia: {w}" for w in words]
    embeddings = model.encode(
        framed_words,
        batch_size=256,
        show_progress_bar=True,
        normalize_embeddings=True
    )
    embeddings = np.array(embeddings, dtype=np.float32)

    print(f"Embeddings shape: {embeddings.shape}")
    np.save(out_npy_path, embeddings)
    print(f"Saved numpy embeddings to {out_npy_path}")

    with open(out_index_path, "w", encoding="utf-8") as f:
        json.dump(words, f, ensure_ascii=False)
    print(f"Saved vocab index to {out_index_path}")

    if to_db:
        print("Inserting/updating words in database...")
        from app.db.session import SessionLocal
        from app.models.word import Word

        db = SessionLocal()
        try:
            for idx, item in enumerate(vocab):
                norm = item["normalized_word"]
                emb_list = embeddings[idx].tolist()
                
                existing = db.query(Word).filter(Word.normalized_word == norm).first()
                if existing:
                    existing.embedding = emb_list
                    existing.is_secret_eligible = item.get("is_secret_eligible", False)
                    existing.frequency = item.get("frequency", 0)
                else:
                    new_word = Word(
                        word=item["word"],
                        normalized_word=norm,
                        category=item.get("category"),
                        frequency=item.get("frequency", 0),
                        is_secret_eligible=item.get("is_secret_eligible", False),
                        embedding=emb_list
                    )
                    db.add(new_word)
                if idx % 1000 == 0:
                    db.commit()
            db.commit()
            print("Database successfully populated with words and embeddings.")
        finally:
            db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--to-db", action="store_true", help="Also sync embeddings to PostgreSQL pgvector")
    args = parser.parse_args()
    generate_and_save_embeddings(to_db=args.to_db)
