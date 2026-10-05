import re
import unicodedata
from typing import Optional

# Indonesian common stopwords / function words (ineligible as secret words)
INDONESIAN_STOPWORDS = {
    "yang", "di", "ke", "dari", "dan", "atau", "ini", "itu", "untuk", "pada",
    "adalah", "sebagai", "oleh", "dengan", "akan", "telah", "sudah", "bisa",
    "dapat", "mereka", "kita", "kami", "kamu", "anda", "dia", "ia", "beliau",
    "kalian", "saya", "aku", "nya", "dalam", "atas", "bawah", "luar", "antara",
    "bagi", "secara", "karena", "sebab", "jika", "kalau", "apabila", "walau",
    "meski", "namun", "tetapi", "tapi", "hanya", "cuma", "juga", "pun", "saja",
    "lagi", "masih", "belum", "tidak", "bukan", "tanpa", "sangat", "lebih",
    "paling", "amat", "sekali", "seperti", "bagaikan", "ibarat", "hingga",
    "sampai", "sejak", "lalu", "kemudian", "ketika", "saat", "waktu", "mana",
    "siapa", "apa", "kapan", "mengapa", "kenapa", "bagaimana", "berapa",
    "dong", "sih", "deh", "kan", "kok", "yah", "yuk", "nih", "tuh", "lah"
}

# Regex to allow Indonesian characters and hyphen for reduplication (e.g. kupu-kupu)
VALID_WORD_PATTERN = re.compile(r'^[a-z]+(-[a-z]+)?$')


def normalize_word(text: str) -> Optional[str]:
    """
    Normalizes Indonesian text:
    - Unicode NFKC normalization
    - Lowercase
    - Strip whitespaces
    - Strip surrounding punctuation
    - Preserve valid reduplication (e.g., kupu-kupu)
    - Returns None if empty or invalid
    """
    if not text or not isinstance(text, str):
        return None

    # Unicode normalization
    normalized = unicodedata.normalize("NFKC", text).strip().lower()

    # Remove extra spaces inside or around
    normalized = re.sub(r'\s+', ' ', normalized)

    # Trim any leading/trailing non-alphanumeric chars
    normalized = normalized.strip(".,!?:;\"'()[]{}<>/\\|@#$%^&*~`_+=0123456789")

    # Replace multiple hyphens with single
    normalized = re.sub(r'-+', '-', normalized)

    # Validate against Indonesian word pattern
    if not normalized or len(normalized) < 2 or len(normalized) > 35:
        return None

    if not VALID_WORD_PATTERN.match(normalized):
        return None

    return normalized


def is_valid_word(word: str) -> bool:
    """Checks if a normalized word is valid syntax for the game."""
    if not word or not isinstance(word, str):
        return False
    return bool(VALID_WORD_PATTERN.match(word)) and 2 <= len(word) <= 35


def is_secret_word_candidate(word: str) -> bool:
    """
    Checks if word is suitable as a daily secret word:
    - Valid word format
    - Length between 3 and 15 letters
    - Not in stopword list
    - Not pure particle or interjection
    """
    norm = normalize_word(word)
    if not norm:
        return False
    if norm in INDONESIAN_STOPWORDS:
        return False
    if len(norm) < 3 or len(norm) > 15:
        return False
    return True
