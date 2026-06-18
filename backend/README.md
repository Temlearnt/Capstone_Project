# Recruitly Backend API

Backend untuk aplikasi Recruitly - AI-powered CV screening dan candidate ranking system.

## 🚀 Fitur

- ✅ Autentikasi HR dengan register/login dan JWT
- ✅ Upload CV PDF (single atau multiple)
- ✅ Input Job Description dan pemrosesan screening
- ✅ Ekstraksi teks dari PDF
- ✅ Matching CV dengan JD menggunakan scoring berbasis TF-IDF / similarity
- ✅ Ranking kandidat otomatis
- ✅ Riwayat screening dan progress status
- ✅ Integrasi dengan Supabase (PostgreSQL + Storage)
- ✅ Endpoint dashboard, kandidat, profil, dan job roles

---

## 📚 Dokumentasi API

**Dokumentasi API lengkap tersedia secara interaktif melalui Swagger UI:**

👉 **[Swagger UI](http://localhost:8000/docs)** - Eksplorasi dan testing semua endpoint secara langsung  

> **Catatan:** Semua daftar endpoint, skema request/response, dan contoh penggunaan tersedia di Swagger UI. Untuk testing API, Anda dapat menggunakan Swagger UI langsung dari browser tanpa perlu tools tambahan.

---

## 🛠️ Tech Stack

| Komponen | Teknologi |
|----------|-----------|
| Framework | FastAPI 0.115.0 |
| Server | Uvicorn |
| Database | Supabase (PostgreSQL) |
| PDF Extraction | PyMuPDF, PyPDF2 |
| Machine Learning | scikit-learn, spaCy |
| Authentication | JWT + bcrypt |
| Deployment | Railway |
| Environment | python-dotenv |
| Experiment Tracking | MLflow |

---

## 📋 Prasyarat

- Python 3.11 atau 3.12
- pip
- Supabase account
- Git (opsional)

---

## 🚀 Cara Menjalankan (Local Development)

### 1. Masuk ke folder backend

```bash
cd backend
```

### 2. Buat virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup environment file

Salin template file `.env .example` menjadi `.env`.

```bash
# Windows
copy ".env .example" .env

# Mac / Linux
cp ".env .example" .env
```

Edit file `.env` dan isi konfigurasi yang diperlukan.

**Contoh konfigurasi:**

```env
APP_ENV=development
DEBUG=True
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-public-key

MLFLOW_TRACKING_URI=file:mlruns
MLFLOW_EXPERIMENT_NAME=recruitly-matching

MAX_UPLOAD_SIZE_MB=50
TEMP_UPLOAD_DIR=uploads

JWT_SECRET_KEY=your-super-secret-key-change-me
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

> **Catatan:** Jika `SUPABASE_BUCKET` tidak diset, backend akan menggunakan default `cv-uploads`.

### 5. Jalankan server

```bash
uvicorn app.main:app --reload
```

Server akan berjalan di `http://localhost:8000`

### 6. Akses dokumentasi API

Buka browser dan akses:

```text
📘 Swagger UI: http://localhost:8000/docs
```

---

## 🚅 Deployment ke Railway

Backend ini dapat dideploy menggunakan Railway dengan konfigurasi yang sudah disiapkan di `railway.json`.

### Konfigurasi Railway

File `railway.json`:

```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
  }
}
```

### Langkah Deployment

1. **Push repository ke GitHub**

2. **Hubungkan ke Railway**
   - Login ke [Railway](https://railway.app)
   - Klik "New Project" → "Deploy from GitHub repo"
   - Pilih repository Anda

3. **Set Environment Variables**
   - Tambahkan semua variabel yang ada di `.env` ke Railway dashboard
   - Railway akan otomatis menyediakan variabel `PORT`

4. **Deploy**
   - Railway akan otomatis melakukan build dan deploy
   - Aplikasi akan berjalan di URL yang disediakan Railway

### Verifikasi Deployment

Setelah deploy selesai, akses:

```text
https://your-app.railway.app/docs
```

---

## 📁 Struktur Folder

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # Entry point aplikasi
│   ├── config.py            # Konfigurasi aplikasi
│   ├── dependencies.py      # Dependency injection
│   ├── storage.py           # Supabase storage handler
│   ├── routers/             # Endpoint handlers
│   │   ├── auth.py
│   │   ├── screen.py
│   │   ├── dashboard.py
│   │   ├── job_roles.py
│   │   ├── profile.py
│   │   ├── candidates.py
│   │   └── ...
│   ├── services/            # Business logic
│   ├── db/                  # Database models & queries
│   └── utils/               # Helper functions
├── requirements.txt
├── .env
├── ".env .example"
├── railway.json
└── mlflow_server.py
```

---

## 🔐 Autentikasi

Semua endpoint (kecuali `/auth/register`, `/auth/login`, `/health`, dan `/docs`) memerlukan token JWT.

**Cara menggunakan token:**

1. Register atau login untuk mendapatkan token
2. Pada Swagger UI, klik tombol **Authorize** di pojok kanan atas
3. Masukkan token dengan format: `Bearer <your-token>`
4. Semua request akan otomatis menyertakan token

---

## 🔧 Environment Variables

| Variable | Deskripsi | Required |
|----------|-----------|----------|
| `SUPABASE_URL` | URL project Supabase | ✅ |
| `SUPABASE_KEY` | Anon/public key Supabase | ✅ |
| `JWT_SECRET_KEY` | Secret key untuk JWT | ✅ |
| `JWT_ALGORITHM` | Algoritma JWT (default: HS256) | ❌ |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Masa berlaku token (default: 1440) | ❌ |
| `CORS_ORIGINS` | Daftar origin yang diizinkan (comma separated) | ❌ |
| `MAX_UPLOAD_SIZE_MB` | Maksimal ukuran upload (default: 50) | ❌ |
| `TEMP_UPLOAD_DIR` | Direktori temporary upload (default: uploads) | ❌ |
| `APP_ENV` | Environment (development/production) | ❌ |
| `DEBUG` | Mode debug (True/False) | ❌ |
| `MLFLOW_TRACKING_URI` | URI tracking MLflow | ❌ |

---

## 🧪 Testing

### Testing Manual dengan Swagger UI

1. Jalankan server lokal
2. Buka `http://localhost:8000/docs`
3. Test setiap endpoint secara interaktif

### Testing dengan cURL

Untuk testing menggunakan cURL, ikuti langkah-langkah:

1. **Register**: `POST /auth/register`
2. **Login**: `POST /auth/login` → dapatkan token
3. **Gunakan token**: Tambahkan header `Authorization: Bearer <token>` pada request berikutnya

> **Catatan:** Semua contoh request lengkap tersedia di Swagger UI.

---

## 📊 Monitoring & Logging

- **Logs**: Aplikasi menggunakan logging bawaan FastAPI
- **Health Check**: `GET /health` untuk mengecek status server
- **Database**: `GET /test/db` untuk mengecek koneksi Supabase
- **MLflow**: Tracking experiment tersedia di `MLFLOW_TRACKING_URI`

---

## 🐛 Troubleshooting

### Error: "Supabase bucket not found"
**Solusi:** Buat bucket `cv-uploads` di Supabase Storage dashboard.

### Error: "Invalid JWT token"
**Solusi:** 
- Pastikan token valid dan belum kadaluwarsa
- Token default berlaku 1440 menit (1 hari)
- Login ulang untuk mendapatkan token baru

### Error: "Failed to extract PDF text"
**Solusi:** 
- Pastikan file PDF tidak corrupted
- Periksa izin baca file PDF
- Coba dengan file PDF lain yang diketahui valid

### Error: "Connection refused" pada deployment
**Solusi:** 
- Pastikan environment variables sudah diset lengkap
- Periksa logs di Railway dashboard
- Verifikasi URL Supabase dan key yang digunakan

---

## 👥 Tim

- **Capstone Project**: PJK-GM048
- **Recruitly Team**

---
