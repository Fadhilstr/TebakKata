import os
import json
import logging
from typing import Dict, Tuple, Optional, List
import numpy as np

from app.core.config import settings
from app.semantic.normalizer import normalize_word

logger = logging.getLogger("konteks.semantic")


class SemanticEngine:
    def __init__(self, data_dir: Optional[str] = None):
        if data_dir is None:
            candidates = [
                "/app/data/vocabulary",
                os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "vocabulary")),
                os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "vocabulary")),
            ]
            data_dir = candidates[1]
            for c in candidates:
                if os.path.exists(c):
                    data_dir = c
                    break
        self.data_dir = data_dir

        self.words: List[str] = []
        self.word_to_idx: Dict[str, int] = {}
        self.embeddings: Optional[np.ndarray] = None
        self._model = None
        self._daily_rank_cache: Dict[str, Dict[str, Tuple[int, float]]] = {}

        self.load_precomputed_data()

    def load_precomputed_data(self):
        index_path = os.path.join(self.data_dir, "vocab_index.json")
        npy_path = os.path.join(self.data_dir, "embeddings.npy")

        if os.path.exists(index_path) and os.path.exists(npy_path):
            logger.info("Loading precomputed vocab index and embeddings...")
            with open(index_path, "r", encoding="utf-8") as f:
                self.words = json.load(f)
            self.word_to_idx = {w: i for i, w in enumerate(self.words)}
            self.embeddings = np.load(npy_path)
            logger.info("Loaded %d words and embeddings matrix %s", len(self.words), self.embeddings.shape)
        else:
            logger.warning("Precomputed embeddings not found at %s. Will load from vocab JSON or on-demand.", npy_path)
            # Try to load raw vocab list if available
            vocab_json = os.path.join(self.data_dir, "game_vocabulary.json")
            if os.path.exists(vocab_json):
                with open(vocab_json, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.words = [item["normalized_word"] for item in data]
                self.word_to_idx = {w: i for i, w in enumerate(self.words)}
                logger.info("Loaded %d vocabulary words without precomputed embeddings.", len(self.words))

    @property
    def model(self):
        """Lazy loader for SentenceTransformer model."""
        if self._model is None:
            logger.info("Loading SentenceTransformer model: %s", settings.EMBEDDING_MODEL_NAME)
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
        return self._model

    def encode_words(self, words_list: List[str]) -> np.ndarray:
        """Encodes list of words into normalized embeddings with Indonesian contextual framing."""
        framed_list = [f"kata bahasa Indonesia: {w}" for w in words_list]
        embs = self.model.encode(framed_list, normalize_embeddings=True, show_progress_bar=False)
        return np.array(embs, dtype=np.float32)

    def is_word_in_vocab(self, word: str) -> bool:
        norm = normalize_word(word)
        return norm is not None and norm in self.word_to_idx

    def calculate_similarity(self, word1: str, word2: str) -> float:
        norm1 = normalize_word(word1)
        norm2 = normalize_word(word2)
        if not norm1 or not norm2:
            return 0.0
        if norm1 == norm2:
            return 1.0

        if self.embeddings is not None and norm1 in self.word_to_idx and norm2 in self.word_to_idx:
            idx1 = self.word_to_idx[norm1]
            idx2 = self.word_to_idx[norm2]
            v1 = self.embeddings[idx1]
            v2 = self.embeddings[idx2]
            return float(np.dot(v1, v2))

        # Dynamic fallback
        v = self.encode_words([norm1, norm2])
        return float(np.dot(v[0], v[1]))

    def get_or_create_daily_rank_map(self, secret_word: str) -> Dict[str, Tuple[int, float]]:
        norm_secret = normalize_word(secret_word)
        if not norm_secret:
            raise ValueError(f"Invalid secret word: {secret_word}")

        if norm_secret in self._daily_rank_cache:
            return self._daily_rank_cache[norm_secret]

        logger.info("Generating global ranking map for secret word: '%s'", norm_secret)
        
        # Ensure we have embeddings
        if self.embeddings is None:
            if not self.words:
                raise RuntimeError("No vocabulary loaded in SemanticEngine")
            logger.info("Computing embeddings on the fly for %d words...", len(self.words))
            self.embeddings = self.encode_words(self.words)

        if norm_secret in self.word_to_idx:
            secret_idx = self.word_to_idx[norm_secret]
            secret_vec = self.embeddings[secret_idx]
        else:
            # If secret word is outside vocabulary index, encode it
            secret_vec = self.encode_words([norm_secret])[0]

        # Vectorized dot product (cosine similarity since normalized)
        similarities = np.dot(self.embeddings, secret_vec)

        # Force secret word itself to 1.00000
        if norm_secret in self.word_to_idx:
            similarities[self.word_to_idx[norm_secret]] = 1.0

        # Hybrid Scoring: boost curated relations if present in database
        try:
            from app.db.session import SessionLocal
            from app.models.word import Word
            from app.models.word_relation import WordRelation

            with SessionLocal() as db:
                secret_word_rec = db.query(Word).filter(Word.normalized_word == norm_secret).first()
                if secret_word_rec:
                    relations = db.query(WordRelation).filter(
                        (WordRelation.word_id == secret_word_rec.id) | 
                        (WordRelation.related_word_id == secret_word_rec.id)
                    ).all()
                    for rel in relations:
                        target_id = rel.related_word_id if rel.word_id == secret_word_rec.id else rel.word_id
                        target_rec = db.query(Word).filter(Word.id == target_id).first()
                        if target_rec and target_rec.normalized_word in self.word_to_idx:
                            t_idx = self.word_to_idx[target_rec.normalized_word]
                            boost = 0.05 * float(rel.weight)
                            similarities[t_idx] = min(0.9999, float(similarities[t_idx]) + boost)
        except Exception as e:
            logger.debug("Optional relation boost skipped: %s", e)

        # Sort descending
        sorted_indices = np.argsort(-similarities)

        rank_map = {}
        for rank_0, idx in enumerate(sorted_indices):
            w = self.words[idx]
            sim = float(similarities[idx])
            rank = rank_0 + 1
            rank_map[w] = (rank, round(sim, 4))

        # Ensure secret word is rank #1
        rank_map[norm_secret] = (1, 1.0)

        # Cache in memory
        self._daily_rank_cache[norm_secret] = rank_map
        logger.info("Global rank map generated: %d ranked words for '%s'", len(rank_map), norm_secret)
        return rank_map

    def evaluate_guess(self, secret_word: str, guess_word: str) -> Optional[Tuple[int, float]]:
        """
        Evaluates a guess against secret_word.
        Returns (ranking, similarity) or None if word is unknown.
        """
        norm_guess = normalize_word(guess_word)
        if not norm_guess:
            return None

        rank_map = self.get_or_create_daily_rank_map(secret_word)
        if norm_guess in rank_map:
            return rank_map[norm_guess]

        # Word is not in the game's dictionary
        return None


# Global singleton instance
semantic_engine = SemanticEngine()
