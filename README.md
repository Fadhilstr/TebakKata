# Konteks Indonesia 🇮

Game web tebak kata berbasis **Semantic Similarity (NLP)** dalam Bahasa Indonesia, terinspirasi oleh mekanisme gameplay Contexto, dibangun dengan identitas orisinal, vocabulary terkurasi, dan arsitektur modern.

Pemain harus menemukan **satu kata rahasia harian** berdasarkan kedekatan makna/konteks kata yang ditebak. Semakin kecil angka rankingnya (misal: `#12`, `#3`), semakin dekat kata tebakan dengan kata rahasia. Peringkat **#1** adalah kata rahasia!

---

## Tech Stack

- **Frontend**: Vue 3 (Composition API), Vite, TypeScript, Tailwind CSS, Canvas-Confetti
- **Backend**: Python 3.12, FastAPI, SQLAlchemy 2, Alembic, Pydantic v2
- **Database & Vektor**: PostgreSQL 16 + `pgvector`
- **NLP / Embedding Model**: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (384-dimensional normalized vectors)
- **Infrastructure**: Docker, Docker Compose, Nginx Reverse Proxy
- **Zona Waktu**: `Asia/Jakarta` (WIB, UTC+7)

---

## Arsitektur Sistem

```text
Browser (Client)
      │
      ▼
Nginx Reverse Proxy (:80)
   ├── /api/  ──► FastAPI Backend (:8000)
   │                  ├── PostgreSQL 16 + pgvector (:5432)
   │                  └── In-Memory Semantic Ranking Matrix
   └── /      ──► Vue 3 + Vite Frontend (:80)
```

---

## Menjalankan Aplikasi (Cara Cepat dengan Docker)

Cukup satu perintah untuk membangun dan menjalankan seluruh stack:

```bash
docker compose up --build
```

Setelah container berjalan:
- Buka browser di: **`http://localhost`**
- API Documentation (Swagger UI): **`http://localhost/api/docs`**

---

## Menjalankan Secara Lokal (Development)
### Prasyarat
- Python 3.12+
- Node.js 20+ & npm
- Docker (untuk PostgreSQL + pgvector)

### 1. Database (PostgreSQL + pgvector)
Jalankan container database:
```bash
docker compose up -d db
```

### 2. Backend
Masuk ke direktori backend:
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Menjalankan migrasi database
alembic upgrade head

# Menyiapkan vocabulary dan embedding
python scripts/prepare_vocabulary.py
python scripts/seed_database.py

# Menjalankan server FastAPI
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend
Masuk ke direktori frontend di terminal terpisah:
```bash
cd frontend
npm install
npm run dev
```
Buka `http://localhost:5173` di browser.

---

## Menjalankan Pengujian (Testing)

Untuk menjalankan seluruh unit dan integration test:

```bash
cd backend
pytest tests/ -v
```

Cakupan pengujian meliputi:
1. `test_normalizer.py`: Normalisasi huruf, pembersihan tanda baca, penanganan kata ulang (*kupu-kupu*), dan filter stopwords.
2. `test_semantic_ranking.py`: Verifikasi bahwa kata rahasia selalu rank #1, uji determinisme, dan sanity check semantik (*kucing* dekat *anjing*, *laut* dekat *pantai*).
3. `test_timezone.py`: Verifikasi kepatuhan zona waktu `Asia/Jakarta` (WIB, UTC+7).
4. `test_api_security.py`: Memastikan kata rahasia **tidak pernah bocor** ke frontend sebelum pemain menyelesaikannya, serta sanitasi input SQL injection & spam.

---

## Keamanan & Anti-Cheat

- **Authoritative Backend**: Kata rahasia dan matriks ranking dihitung secara aman di server backend. Daftar kata rahasia tidak pernah di-bundle ke dalam file JavaScript browser.
- **Zero Secret Leakage**: Endpoint `/api/game/today` hanya mengembalikan `game_id` dan tanggal. Kata rahasia hanya dikirimkan kembali pada endpoint tebakan jika pemain berhasil menebaknya secara tepat (`is_correct: true`).
- **Rate Limiting**: Pembatasan laju tebakan per sesi untuk mencegah *dictionary brute-force*.

---

## Lisensi
FADHIL SATRIA WIDODO.
