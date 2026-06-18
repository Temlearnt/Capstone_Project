
# Recruitly Backend API

Backend untuk aplikasi Recruitly - AI-powered CV screening dan candidate ranking system.

## 🚀 Fitur

- ✅ Autentikasi HR (Register, Login, JWT Token)
- ✅ Upload CV (PDF single, multiple, atau ZIP)
- ✅ Input Job Description (teks bebas)
- ✅ Pilih Tipe Pekerjaan (Full Time, Part Time, Intern, Freelance, Contract)
- ✅ Ekstraksi teks dari PDF (PyMuPDF)
- ✅ Matching CV dengan JD (TF-IDF + Cosine Similarity)
- ✅ Ranking kandidat berdasarkan skor
- ✅ Riwayat screening
- ✅ Database Supabase (PostgreSQL)

## 🛠️ Tech Stack

| Komponen | Teknologi |
|----------|-----------|
| Framework | FastAPI 0.115.0 |
| Server | Uvicorn |
| Database | Supabase (PostgreSQL) |
| PDF Extraction | PyMuPDF, pdfplumber (fallback) |
| Machine Learning | scikit-learn (TF-IDF, Cosine Similarity) |
| Authentication | JWT + bcrypt |
| Deployment | Railway |

## 📋 Prasyarat

- Python 3.11 atau 3.12
- pip (Python package manager)
- Supabase account (gratis)
- Git (opsional)

## 🚀 Cara Menjalankan (Local Development)

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/recruitly.git
cd recruitly/backend
```

### 2. Buat Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables

Copy file `.env.example` menjadi `.env`:

```bash
cp .env.example .env
```

Edit file `.env` dan isi dengan nilai yang sesuai:

```env
APP_ENV=development
DEBUG=True
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Supabase (isi dengan credentials asli dari dashboard Supabase)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-public-key

# JWT (ganti dengan secret key yang kuat)
JWT_SECRET_KEY=your-super-secret-key-change-me
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### 5. Setup Database Supabase

1. Buat project di [supabase.com](https://supabase.com)
2. Jalankan SQL schema yang ada di `database/schema.sql` (atau di dokumentasi proyek)
3. Dapatkan `SUPABASE_URL` dan `SUPABASE_KEY` dari Settings → API

### 6. Jalankan Server

```bash
uvicorn app.main:app --reload
```

Server akan berjalan di `http://localhost:8000`

### 7. Akses Dokumentasi API

Buka browser di `http://localhost:8000/docs` untuk melihat Swagger UI.

## 📁 Struktur Folder

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # Entry point FastAPI
│   ├── config.py            # Konfigurasi dari .env
│   ├── dependencies.py      # Dependency injection
│   ├── storage.py           # In-memory storage (development)
│   ├── routers/             # API endpoints
│   │   ├── auth.py          # /auth/register, /auth/login
│   │   ├── screen.py        # /screen (upload, status, result)
│   │   └── ...
│   ├── services/            # Business logic
│   │   ├── pdf_extractor.py # Ekstraksi teks dari PDF
│   │   ├── matching.py      # Hitung skor CV vs JD
│   │   └── entity_extractor.py # Ekstrak nama, email, skill
│   ├── db/                  # Database layer
│   │   ├── supabase_client.py
│   │   └── operations.py
│   └── utils/               # Utility functions
│       └── auth.py          # JWT helper
├── ml_models/               # Model ML (.pkl)
├── requirements.txt
├── Dockerfile
└── .env.example
```

## 🔌 API Endpoints

### Authentication
| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| POST | `/auth/register` | Registrasi user baru |
| POST | `/auth/login` | Login dapat JWT token |
| GET | `/auth/me` | Ambil data user |

### Screening
| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| POST | `/screen` | Upload CV + JD, mulai screening |
| GET | `/screen/{id}/status` | Cek status screening |
| GET | `/screen/{id}/result` | Ambil hasil ranking |
| GET | `/screen/history` | Riwayat screening |

### Utility
| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| GET | `/health` | Cek status server |
| GET | `/docs` | Swagger UI documentation |

## 🧪 Contoh Request

### Register

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "hr@company.com",
    "password": "rahasia123",
    "full_name": "Budi Santoso",
    "company_name": "PT Teknologi Maju"
  }'
```

### Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "hr@company.com",
    "password": "rahasia123"
  }'
```

### Screening CV

```bash
curl -X POST http://localhost:8000/screen \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "job_description=Kami mencari backend engineer dengan Python" \
  -F "employment_type=fulltime" \
  -F "files=@cv1.pdf" \
  -F "files=@cv2.pdf"
```

### Cek Hasil

```bash
curl -X GET http://localhost:8000/screen/SCREENING_ID/result
```

## 👥 Tim

- Capstone Project PJK-GM048
- Recruitly Team
