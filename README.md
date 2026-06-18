# Recruitly

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![ONNX](https://img.shields.io/badge/ONNX-005CED?style=for-the-badge&logo=onnx&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white)
![Railway](https://img.shields.io/badge/Railway-0B0D0E?style=for-the-badge&logo=railway&logoColor=white)
![Vercel](https://img.shields.io/badge/Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white)
![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)
![Scikit-Learn](https://img.shields.io/badge/Scikit_Learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white)

> AI-Powered CV Screening & Candidate Ranking System

## 📖 Tentang Recruitly

**Recruitly** adalah aplikasi web berbasis AI yang membantu HR (Human Resources) melakukan screening CV secara otomatis dan objektif. Aplikasi ini mengekstrak informasi penting dari CV, mencocokkan dengan job description, dan menghasilkan ranking kandidat berdasarkan skor kesesuaian.

### 🎯 Masalah yang Diselesaikan
- ❌ Screening CV manual memakan waktu berjam-jam
- ❌ Penilaian HR tidak konsisten dan rentan bias
- ❌ Kandidat berkualitas potensial terlewat karena keterbatasan waktu

### ✅ Solusi yang Ditawarkan
- ✅ Otomatisasi screening CV dengan NLP
- ✅ Ranking kandidat objektif berdasarkan skor kesesuaian
- ✅ Proses cepat: puluhan CV dalam hitungan menit

---

## ⚙️ Cara Kerja

```
┌─────────────────────────────────────────────────────────────────┐
│                      HR UPLOAD CV & JD                          │
└───────────────────────────────┬─────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│                    PDF EXTRACTION (PyMuPDF)                     │
│                    Teks diekstrak dari CV                        │
└───────────────────────────────┬─────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│                      TEXT CLEANING                               │
│              Lowercase, hapus stopwords & punctuation           │
└───────────────────────────────┬─────────────────────────────────┘
                                ↓
              ┌─────────────────┴─────────────────┐
              ↓                                   ↓
┌─────────────────────────┐         ┌─────────────────────────┐
│     NER (ONNX)          │         │    SBERT (ONNX)         │
│ Ekstrak:                │         │ Ubah teks ke vektor      │
│ - Nama, Email           │         │ embedding                │
│ - Skills                │         │ (semantic representation)│
│ - Pengalaman            │         └───────────┬─────────────┘
│ - Pendidikan            │                     │
└───────────┬─────────────┘                     │
            ↓                                   ↓
┌─────────────────────────┐         ┌─────────────────────────┐
│   Data Kandidat         │         │  Vektor CV & JD         │
│   (terstruktur)         │         │  (numerik)              │
└───────────┬─────────────┘         └───────────┬─────────────┘
            └─────────────────┬─────────────────┘
                              ↓
              ┌─────────────────────────────┐
              │    COSINE SIMILARITY        │
              │  Hitung skor kesesuaian     │
              │  (0-100%)                   │
              └───────────────┬─────────────┘
                              ↓
              ┌─────────────────────────────┐
              │       RANKING               │
              │  Urutkan dari skor tertinggi│
              └───────────────┬─────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      HASIL RANKING                              │
│   Tabel kandidat: Rank | Nama | Skor | Skills | Status         │
└─────────────────────────────────────────────────────────────────┘
```

---

## ✨ Fitur

| No | Fitur | Deskripsi |
|----|-------|-----------|
| 1 | **Autentikasi HR** | Register, login, JWT token, isolasi data per perusahaan |
| 2 | **Upload CV** | Support file PDF (single/multiple) dan ZIP (batch) |
| 3 | **Input Job Description** | HR tulis JD bebas atau pilih template role |
| 4 | **Ekstraksi CV (NER)** | Ekstrak nama, email, skills, pengalaman, pendidikan |
| 5 | **Matching CV-JD** | SBERT ONNX + Cosine Similarity untuk hitung skor |
| 6 | **Ranking Kandidat** | Urutkan kandidat dari skor tertinggi ke terendah |
| 7 | **Riwayat Screening** | Semua sesi screening tersimpan permanen di Supabase |
| 8 | **Dashboard HR** | Statistik ringkasan, top 5 kandidat, distribusi skill |
| 9 | **Proses Asynchronous** | Screening berjalan di background, HR pantau progress |
| 10 | **Multi-tenant** | Data antar perusahaan terisolasi |

---

## 📁 Struktur Folder

### 📂 Struktur Backend

```
backend/
├── app/                          # Kode utama aplikasi
│   ├── db/                       # Database layer (koneksi Supabase)
│   ├── models/                   # Model ONNX (SBERT, NER)
│   ├── routers/                  # API endpoints
│   ├── services/                 # Business logic
│   ├── utils/                    # Utility functions (auth, JWT)
│   ├── config.py                 # Konfigurasi environment
│   ├── dependencies.py           # Dependency injection
│   ├── main.py                   # Entry point FastAPI
│   └── storage.py                # In-memory storage (development)
│
├── database/                     # Skema database
│   └── db.sql                    # Supabase schema
│
├── venv/                         # Virtual environment
├── .env                          # Environment variables (RAHASIA)
├── .env.example                  # Template environment
├── requirements.txt              # Dependencies Python
└── railway.json                  # Konfigurasi Railway
```

### 📂 Struktur Frontend

```
frontend/
├── index.html                    # Halaman utama
├── login.html                    # Halaman login/register
├── dashboard.html                # Halaman dashboard HR
├── css/
│   └── style.css                 # Styling custom
├── js/
│   └── api.js                    # Panggilan ke backend
└── assets/                       # Gambar, icon, dll
```

### 📂 Struktur Model

```
model/
├── sbert_embedding_quantized.onnx    # SBERT untuk semantic embedding
└── ner_model_quantized.onnx          # NER untuk ekstraksi entities
```

---

## 🚀 Cara Menggunakan

### 1. Clone Repository

```bash
git clone https://github.com/Temlearnt/backend-recruitly.git
cd backend-recruitly
```

### 3. Setup Model 

```bash
cd ../model
```
Lihat di /model/README.md

### 3. Setup Backend

```bash
cd backend
```
Lihat di /backend/README.md

### 4. Setup Frontend

```bash
cd ../frontend
```
Lihat di /frontend/README.md


### 4. Registrasi HR

Buka `http://localhost:3000/login.html` (atau port Live Server), klik tab **Register**, isi data:

- Email: `hr@company.com`
- Password: `rahasia123`
- Nama Lengkap: `Budi Santoso`
- Nama Perusahaan: `PT Teknologi Maju`

### 5. Login dan Screening

1. Login dengan email dan password di atas
2. Upload file CV (PDF atau ZIP)
3. Isi Job Description
4. Klik **Mulai Screening**
5. Tunggu proses selesai, lihat hasil ranking

---

## 🚢 Deployment

### Backend (Railway)

1. Push kode ke GitHub (pastikan `.env` tidak di-commit)
2. Buat project di Railway → Deploy from GitHub
3. Set Root Directory ke `backend`
4. Tambahkan environment variables di Railway:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `JWT_SECRET_KEY`
5. Deploy

### Frontend (Vercel)

1. Push kode ke GitHub
2. Import project ke Vercel
3. Set Root Directory ke `frontend`
4. Tambahkan environment variable:
   - `VITE_API_URL` = URL backend Railway
5. Deploy

---

## 👥 Tim Pengembang

| <img src="https://ui-avatars.com/api/?name=Putu&background=667eea&color=fff&size=100" width="100"> | <img src="https://ui-avatars.com/api/?name=Ryan&background=667eea&color=fff&size=100" width="100"> | <img src="https://ui-avatars.com/api/?name=Ilyas&background=667eea&color=fff&size=100" width="100"> | <img src="https://ui-avatars.com/api/?name=Afif&background=667eea&color=fff&size=100" width="100"> |
|:---:|:---:|:---:|:---:|
| **I Putu Sutha Satyawan** | **Ryan Nanda Saputra Haryanto** | **Ilyas Lucky Firmansyah** | **Muhammad Fathir Afif** |
| Backend Engineer (AI Engineer) | Data Engineer (AI Engineer) | NLP Engineer (AI Engineer) | Frontend Engineer (AI Engineer) |
| API, proses data, integrasi model | Kumpulkan dan preprocessing dataset | Pembuatan model untuk ekstraksi dan embedding| Desain user interface |

---

<div align="center">
  <sub>Built with by Recruitly Team | Capstone Project</sub>
</div>
```

