import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.semantic.normalizer import INDONESIAN_STOPWORDS, is_valid_word


def validate():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    json_path = os.path.join(root_dir, "data", "vocabulary", "cleaned_vocabulary.json")

    assert os.path.exists(json_path), f"File {json_path} does not exist"

    with open(json_path, "r", encoding="utf-8") as f:
        words = json.load(f)

    print(f"Total vocabulary loaded: {len(words)}")

    seen = set()
    secret_count = 0
    test_words = ["laut", "pantai", "gunung", "kucing", "anjing", "kopi", "rumah", "dokter", "hujan"]
    found_tests = set()

    for item in words:
        w = item["normalized_word"]
        assert w not in seen, f"Duplicate found: {w}"
        seen.add(w)

        assert is_valid_word(w), f"Invalid word format: {w}"

        if item["is_secret_eligible"]:
            secret_count += 1
            assert w not in INDONESIAN_STOPWORDS, f"Stopword in secret pool: {w}"

        if w in test_words:
            found_tests.add(w)

    print(f"Unique words: {len(seen)}")
    print(f"Secret-eligible words: {secret_count}")
    print(f"Test words found: {len(found_tests)}/{len(test_words)}: {found_tests}")

    assert len(found_tests) == len(test_words), f"Missing test words: {set(test_words) - found_tests}"
    assert secret_count >= 500, f"Too few secret words: {secret_count}"
    assert len(words) >= 10000, f"Vocabulary too small: {len(words)}"

    print("ALL VOCABULARY VALIDATION CHECKS PASSED!")


if __name__ == "__main__":
    validate()
