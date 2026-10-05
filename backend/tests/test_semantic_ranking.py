import pytest
from app.semantic.engine import SemanticEngine
from app.semantic.normalizer import normalize_word


@pytest.fixture(scope="module")
def engine():
    eng = SemanticEngine()
    # If precomputed not available in test run, create a mini vocabulary
    if not eng.words or eng.embeddings is None:
        sample_words = [
            "laut", "pantai", "ombak", "samudra", "air", "pasir", "ikan",
            "kucing", "anjing", "hewan", "peliharaan", "bulu",
            "dokter", "rumah", "rumah sakit", "obat", "pasien",
            "komputer", "pensil", "jalan", "meja", "kursi"
        ]
        eng.words = [normalize_word(w) for w in sample_words if normalize_word(w)]
        eng.word_to_idx = {w: i for i, w in enumerate(eng.words)}
        eng.embeddings = eng.encode_words(eng.words)
    return eng


def test_secret_word_is_always_rank_one(engine):
    secret = "laut"
    res = engine.evaluate_guess(secret, "laut")
    assert res is not None
    rank, sim = res
    assert rank == 1
    assert sim == 1.0


def test_semantic_sanity_checks(engine):
    # Laut should be closer to pantai than to komputer
    sim_pantai = engine.calculate_similarity("laut", "pantai")
    sim_komputer = engine.calculate_similarity("laut", "komputer")
    assert sim_pantai > sim_komputer, f"Expected sim(laut, pantai) > sim(laut, komputer), got {sim_pantai} vs {sim_komputer}"

    # Kucing should be closer to anjing than to meja
    sim_anjing = engine.calculate_similarity("kucing", "anjing")
    sim_meja = engine.calculate_similarity("kucing", "meja")
    assert sim_anjing > sim_meja, f"Expected sim(kucing, anjing) > sim(kucing, meja), got {sim_anjing} vs {sim_meja}"


def test_ranking_determinism(engine):
    secret = "kucing"
    res1 = engine.evaluate_guess(secret, "anjing")
    res2 = engine.evaluate_guess(secret, "anjing")
    assert res1 == res2, "Ranking calculation must be deterministic"


def test_unknown_word_handling(engine):
    secret = "laut"
    # Random non-existent word
    res = engine.evaluate_guess(secret, "xyzqwertyuiop")
    # If not valid or outside vocab, engine handles safely
    assert res is None or isinstance(res[0], int)
