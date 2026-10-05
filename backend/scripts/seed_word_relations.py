import os
import sys
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import SessionLocal
from app.models.word import Word
from app.models.word_relation import WordRelation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed_relations")

CURATED_RELATIONS = [
    # halaman
    ("halaman", "pekarangan", "synonym", 1.0),
    ("halaman", "taman", "contextual", 0.95),
    ("halaman", "teras", "contextual", 0.85),
    ("halaman", "rumah", "contextual", 0.85),
    ("halaman", "pelataran", "synonym", 1.0),
    ("halaman", "buku", "contextual", 0.95),
    ("halaman", "lembar", "contextual", 0.95),
    ("halaman", "kertas", "contextual", 0.85),
    ("halaman", "bab", "contextual", 0.85),
    ("halaman", "paragraf", "contextual", 0.80),
    
    # laut
    ("laut", "pantai", "contextual", 1.0),
    ("laut", "samudra", "synonym", 1.0),
    ("laut", "ombak", "contextual", 0.9),
    ("laut", "air", "hypernym", 0.8),
    ("laut", "kapal", "contextual", 0.8),
    ("laut", "ikan", "contextual", 0.8),
    ("laut", "pulau", "contextual", 0.8),
    
    # kucing
    ("kucing", "anjing", "co-hyponym", 0.9),
    ("kucing", "hewan", "hypernym", 1.0),
    ("kucing", "peliharaan", "contextual", 0.9),
    ("kucing", "bulu", "contextual", 0.8),
    ("kucing", "tikus", "contextual", 0.8),
    
    # rumah
    ("rumah", "hunian", "synonym", 1.0),
    ("rumah", "bangunan", "hypernym", 0.9),
    ("rumah", "kamar", "meronym", 0.8),
    ("rumah", "atap", "meronym", 0.8),
]


def seed_relations():
    db = SessionLocal()
    try:
        count = 0
        for w1_text, w2_text, rel_type, weight in CURATED_RELATIONS:
            w1 = db.query(Word).filter(Word.normalized_word == w1_text).first()
            w2 = db.query(Word).filter(Word.normalized_word == w2_text).first()
            if not w1 or not w2:
                continue

            existing = db.query(WordRelation).filter(
                (WordRelation.word_id == w1.id) & (WordRelation.related_word_id == w2.id)
            ).first()
            if not existing:
                rel = WordRelation(
                    word_id=w1.id,
                    related_word_id=w2.id,
                    relation_type=rel_type,
                    weight=weight
                )
                db.add(rel)
                count += 1

        db.commit()
        logger.info("Successfully seeded %d curated word relations.", count)
    finally:
        db.close()


if __name__ == "__main__":
    seed_relations()
