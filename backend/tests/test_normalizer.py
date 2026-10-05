import pytest
from app.semantic.normalizer import normalize_word, is_valid_word, is_secret_word_candidate, INDONESIAN_STOPWORDS


def test_normalization_basics():
    assert normalize_word("Pantai") == "pantai"
    assert normalize_word("  LAUT  ") == "laut"
    assert normalize_word("kucing!") == "kucing"
    assert normalize_word("...rumah...") == "rumah"


def test_normalization_reduplication():
    assert normalize_word("Kupu-kupu") == "kupu-kupu"
    assert normalize_word("laba-laba") == "laba-laba"
    assert normalize_word("anak-anak") == "anak-anak"


def test_normalization_invalid_inputs():
    assert normalize_word("") is None
    assert normalize_word("   ") is None
    assert normalize_word("!@#$%^&*") is None
    assert normalize_word("a") is None  # single char
    assert normalize_word("12345") is None


def test_is_valid_word():
    assert is_valid_word("laut") is True
    assert is_valid_word("kupu-kupu") is True
    assert is_valid_word("123") is False
    assert is_valid_word("rumah makan") is False  # spaces disallowed in single guess


def test_secret_word_candidate():
    assert is_secret_word_candidate("laut") is True
    assert is_secret_word_candidate("kucing") is True
    assert is_secret_word_candidate("dan") is False  # stopword
    assert is_secret_word_candidate("yang") is False  # stopword
    assert is_secret_word_candidate("di") is False  # stopword
