import os
import sys
import json
import re

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.semantic.normalizer import normalize_word, is_secret_word_candidate, INDONESIAN_STOPWORDS

# Curated high-priority concrete daily words list (ensures rich gameplay from day 1)
CURATED_DAILY_SECRETS = {
    # Alam & Geografi
    "laut", "pantai", "gunung", "sungai", "danau", "hutan", "bukit", "lembah", "pulau",
    "samudra", "ombak", "pasir", "karang", "batu", "tanah", "angin", "hujan", "badai",
    "petir", "awan", "matahari", "bulan", "bintang", "langit", "pelangi", "udara",
    "salju", "es", "api", "asap", "debu", "cahaya", "kegelapan", "gempa", "tsunami",
    # Flora & Fauna
    "kucing", "anjing", "burung", "ikan", "kuda", "sapi", "kambing", "ayam", "bebek",
    "singa", "harimau", "gajah", "jerapah", "monyet", "kelinci", "tikus", "ular",
    "buaya", "katak", "kupu-kupu", "lebah", "semut", "nyamuk", "laba-laba", "paus",
    "hiu", "lumba-lumba", "cumi-cumi", "kepiting", "udang", "pohon", "bunga", "daun",
    "akar", "batang", "ranting", "rumput", "mawar", "melati", "anggrek", "buah",
    "biji", "kelapa", "pisang", "mangga", "apel", "jeruk", "semangka", "durian",
    # Makanan & Minuman
    "nasi", "roti", "daging", "telur", "susu", "keju", "mentega", "minyak", "gula",
    "garam", "merica", "kecap", "sambal", "sup", "soto", "sate", "bakso", "mie",
    "kopi", "teh", "jus", "sirup", "madu", "cokelat", "kue", "biskuit", "permen",
    # Rumah & Bangunan
    "rumah", "kamar", "dapur", "toilet", "atap", "pintu", "jendela", "dinding", "lantai",
    "pagar", "taman", "gedung", "kantor", "sekolah", "kampus", "rumah sakit", "pasar",
    "toko", "restoran", "hotel", "stasiun", "bandara", "pelabuhan", "jembatan", "jalan",
    # Benda & Perabotan
    "meja", "kursi", "lemari", "tempat tidur", "kasur", "bantal", "selimut", "lampu",
    "cermin", "jam", "telepon", "komputer", "laptop", "televisi", "kamera", "radio",
    "piring", "gelas", "sendok", "garpu", "pisau", "wajan", "panci", "sapu", "ember",
    "tas", "dompet", "kunci", "buku", "pensil", "pulpen", "kertas", "surat", "amplop",
    # Pakaian & Aksesori
    "baju", "celana", "rok", "jaket", "jas", "sepatu", "sandal", "kaus kaki", "topi",
    "kacamata", "sabuk", "dasi", "cincin", "kalung", "gelang", "jam tangan", "payung",
    # Profesi & Manusia
    "dokter", "perawat", "guru", "dosen", "polisi", "tentara", "pilot", "nahkoda",
    "masinis", "sopir", "petani", "nelayan", "pedagang", "koki", "penulis", "pelukis",
    "musisi", "penyanyi", "atlet", "arsitek", "hakim", "pengacara", "presiden", "raja",
    "ratu", "ayah", "ibu", "anak", "kakak", "adik", "kakek", "nenek", "paman", "bibi",
    # Tubuh
    "kepala", "rambut", "mata", "telinga", "hidung", "mulut", "gigi", "lidah", "bibir",
    "leher", "bahu", "dada", "perut", "punggung", "tangan", "jari", "kaki", "lutut",
    "jantung", "otak", "darah", "tulang", "kulit",
    # Perasaan & Pikiran
    "cinta", "bahagia", "senang", "gembira", "sedih", "marah", "takut", "cemas",
    "rindu", "bangga", "malu", "kecewa", "harapan", "mimpi", "ingatan", "ilmu",
    "keberanian", "kesabaran", "kejujuran", "keadilan", "damai",
    # Waktu & Musim
    "pagi", "siang", "sore", "malam", "fajar", "senja", "hari", "minggu", "bulan",
    "tahun", "abad", "detik", "menit", "jam", "kemarin", "sekarang", "besok",
    # Aktivitas & Gerak
    "makan", "minum", "tidur", "bangun", "jalan", "lari", "lompat", "terbang", "renang",
    "baca", "tulis", "dengar", "lihat", "bicara", "nyanyi", "tari", "main", "kerja",
    "belajar", "masak", "beli", "jual", "bayar", "hitung", "gambar", "tanam", "panen"
}


def load_raw_words(data_dir: str):
    freq_path = os.path.join(data_dir, "raw_frequency_words.txt")
    kbbi_path = os.path.join(data_dir, "raw_kbbi_words.txt")

    words_map = {}  # normalized_word -> {word, freq, is_kbbi}

    # 1. Load frequency words
    if os.path.exists(freq_path):
        print(f"Reading {freq_path}...")
        with open(freq_path, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split()
                if not parts:
                    continue
                raw_w = parts[0]
                freq = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 1
                norm = normalize_word(raw_w)
                if not norm:
                    continue
                if norm not in words_map:
                    words_map[norm] = {"word": norm, "frequency": freq, "is_kbbi": False}
                else:
                    words_map[norm]["frequency"] = max(words_map[norm]["frequency"], freq)

    # 2. Load KBBI words
    if os.path.exists(kbbi_path):
        print(f"Reading {kbbi_path}...")
        with open(kbbi_path, "r", encoding="utf-8") as f:
            for line in f:
                raw_w = line.strip()
                if not raw_w:
                    continue
                norm = normalize_word(raw_w)
                if not norm:
                    continue
                if norm not in words_map:
                    words_map[norm] = {"word": norm, "frequency": 10, "is_kbbi": True}
                else:
                    words_map[norm]["is_kbbi"] = True
                    # Boost frequency for verified dictionary words
                    words_map[norm]["frequency"] = max(words_map[norm]["frequency"], 10)

    return words_map


def clean_and_curate_vocabulary(words_map):
    cleaned = []

    for norm, data in words_map.items():
        # Exclude single character words (except meaningful ones if any)
        if len(norm) < 2:
            continue

        # Filter out common junk / english words that crept into subtitles unless common in ID
        freq = data["frequency"]
        is_kbbi = data["is_kbbi"]

        # If not in KBBI, require a reasonable frequency threshold to avoid OCR typos / names
        if not is_kbbi and freq < 25:
            continue

        # Determine secret word eligibility
        is_secret = False
        if norm in CURATED_DAILY_SECRETS:
            is_secret = True
        elif is_kbbi and freq >= 100 and is_secret_word_candidate(norm):
            # Extra filters for auto-candidate
            # Don't pick verbs with obscure affixes or very high frequency grammar words
            if norm not in INDONESIAN_STOPWORDS:
                is_secret = True

        cleaned.append({
            "word": data["word"],
            "normalized_word": norm,
            "frequency": freq,
            "is_secret_eligible": is_secret,
            "category": "curated" if norm in CURATED_DAILY_SECRETS else ("kbbi" if is_kbbi else "general")
        })

    # Sort primarily by frequency descending
    cleaned.sort(key=lambda x: (x["is_secret_eligible"], x["frequency"]), reverse=True)
    return cleaned


def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    data_dir = os.path.join(root_dir, "data", "vocabulary")
    output_path = os.path.join(data_dir, "cleaned_vocabulary.json")

    print(f"Data directory: {data_dir}")
    words_map = load_raw_words(data_dir)
    print(f"Loaded {len(words_map)} unique normalized raw words.")

    cleaned = clean_and_curate_vocabulary(words_map)
    secret_count = sum(1 for w in cleaned if w["is_secret_eligible"])

    print(f"Cleaned vocabulary: {len(cleaned)} words.")
    print(f"Secret-eligible words: {secret_count} words.")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)

    print(f"Saved cleaned vocabulary to {output_path}")


if __name__ == "__main__":
    main()
