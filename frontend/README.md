# Capstone Project — Recruitly

Recruitly adalah aplikasi web untuk membantu proses screening kandidat. Aplikasi ini menyediakan fitur autentikasi, upload CV, input Job Description, dashboard kandidat, ranking kandidat, detail kandidat, dan halaman profil pengguna.

Project ini menggunakan **React** di sisi frontend dan terhubung ke backend API/FastAPI melalui konfigurasi environment.

---

## Daftar Isi

- [Fitur Utama](#fitur-utama)
- [Tech Stack](#tech-stack)
- [Struktur Project](#struktur-project)
- [Cara Menjalankan Project](#cara-menjalankan-project)
- [Konfigurasi Environment](#konfigurasi-environment)
- [Script yang Tersedia](#script-yang-tersedia)
- [Alur Singkat Aplikasi](#alur-singkat-aplikasi)
- [Catatan Pengembangan](#catatan-pengembangan)

---

## Fitur Utama

- Landing page aplikasi Recruitly.
- Register dan login pengguna.
- Dashboard statistik kandidat.
- Upload CV dan input Job Description.
- Ranking kandidat berdasarkan hasil screening.
- Detail kandidat berisi informasi lengkap kandidat.
- Halaman profil pengguna tanpa fitur foto profil.
- Integrasi API backend melalui service layer.
- Dukungan mode mock API untuk testing tampilan tanpa backend.

---

## Tech Stack

### Frontend

- React 18
- React Scripts
- JavaScript
- CSS
- Lucide React
- Supabase Client

### Backend/API

Frontend disiapkan untuk terhubung ke backend FastAPI melalui environment variable:

```env
REACT_APP_API_URL=http://localhost:8000
```

Jika backend belum tersedia, aplikasi dapat dijalankan menggunakan mock API.

---

## Struktur Project

```text
Capstone_Project/
├── README.md
├── package-lock.json
├── README_FASTAPI_ENV_FIX.txt
│
└── frontend/
    ├── public/
    │   ├── index.html
    │   └── recruitly-logo.png
    │
    ├── src/
    │   ├── assets/
    │   │   ├── recruitly-loading-logo.png
    │   │   ├── recruitly-logo.png
    │   │   ├── recruitly-white-transparent.png
    │   │   ├── team-1.jpeg
    │   │   ├── team-2.jpeg
    │   │   ├── team-3.jpeg
    │   │   └── team-4.jpeg
    │   │
    │   ├── components/
    │   │   ├── auth/
    │   │   │   ├── AuthPage.jsx
    │   │   │   └── AuthPage.css
    │   │   │
    │   │   ├── candidates/
    │   │   │   ├── CandidateDetail.jsx
    │   │   │   ├── CandidateDetail.css
    │   │   │   ├── RankingTable.jsx
    │   │   │   └── RankingTable.css
    │   │   │
    │   │   ├── dashboard/
    │   │   │   ├── Dashboard.jsx
    │   │   │   └── Dashboard.css
    │   │   │
    │   │   ├── layout/
    │   │   │   ├── Sidebar.jsx
    │   │   │   └── Sidebar.css
    │   │   │
    │   │   ├── profile/
    │   │   │   ├── ProfilePage.jsx
    │   │   │   └── ProfilePage.css
    │   │   │
    │   │   ├── ui/
    │   │   │   └── index.jsx
    │   │   │
    │   │   ├── upload/
    │   │   │   ├── UploadPage.jsx
    │   │   │   └── UploadPage.css
    │   │   │
    │   │   ├── LandingPage.jsx
    │   │   └── LandingPage.css
    │   │
    │   ├── data/
    │   │   └── candidates.js
    │   │
    │   ├── hooks/
    │   │   └── useAppContext.jsx
    │   │
    │   ├── pages/
    │   │   ├── Dashboard.jsx
    │   │   ├── Detail.jsx
    │   │   ├── Ranking.jsx
    │   │   └── Upload.jsx
    │   │
    │   ├── services/
    │   │   ├── apiClient.js
    │   │   ├── authService.js
    │   │   ├── candidateService.js
    │   │   ├── nlp.js
    │   │   ├── nlpService.js
    │   │   └── supabaseClient.js
    │   │
    │   ├── utils/
    │   │   └── helpers.js
    │   │
    │   ├── App.jsx
    │   ├── App.css
    │   ├── index.js
    │   ├── index.css
    │   └── main.jsx
    │
    ├── .env.example
    ├── .gitignore
    ├── package.json
    ├── package-lock.json
    ├── index.html
    ├── vite.config.js
    ├── BACKEND_API_CONTRACT.md
    └── FASTAPI_INTEGRATION.md
```

---

## Penjelasan Folder Penting

### `frontend/src/components`

Berisi komponen utama aplikasi yang dipisahkan berdasarkan fitur.

- `auth/` untuk halaman login dan register.
- `dashboard/` untuk tampilan statistik kandidat.
- `candidates/` untuk ranking dan detail kandidat.
- `upload/` untuk upload CV dan input Job Description.
- `profile/` untuk halaman profil pengguna.
- `layout/` untuk sidebar dan layout navigasi.
- `ui/` untuk komponen UI reusable.

### `frontend/src/services`

Berisi logic komunikasi data dan API.

- `apiClient.js` mengatur request ke backend API.
- `authService.js` mengatur login, register, session, dan logout.
- `candidateService.js` mengatur data kandidat dan Job Description.
- `nlp.js` dan `nlpService.js` untuk logic pemrosesan NLP/screening.
- `supabaseClient.js` untuk konfigurasi Supabase.

### `frontend/src/data`

Berisi data kandidat dan Job Description default/dummy yang digunakan aplikasi.

### `frontend/src/assets`

Berisi logo, gambar loading, dan asset visual lain.

---

## Cara Menjalankan Project

### 1. Clone repository

```bash
git clone https://github.com/Temlearnt/Capstone_Project.git
cd Capstone_Project
```

### 2. Masuk ke folder frontend

```bash
cd frontend
```

### 3. Install dependency

```bash
npm install
```

### 4. Buat file `.env`

Copy file `.env.example` menjadi `.env`.

```bash
copy .env.example .env
```

Untuk Mac/Linux:

```bash
cp .env.example .env
```

### 5. Jalankan aplikasi

```bash
npm start
```

Aplikasi akan berjalan di:

```text
http://localhost:3000
```

---

## Konfigurasi Environment

File environment berada di:

```text
frontend/.env
```

Contoh isi:

```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_USE_MOCK_API=false
REACT_APP_SUPABASE_URL=isi_url_supabase
REACT_APP_SUPABASE_ANON_KEY=isi_anon_key_supabase
```

### Penjelasan variable

| Variable | Fungsi |
|---|---|
| `REACT_APP_API_URL` | URL backend API/FastAPI |
| `REACT_APP_USE_MOCK_API` | Mengaktifkan atau mematikan mock API |
| `REACT_APP_SUPABASE_URL` | URL project Supabase |
| `REACT_APP_SUPABASE_ANON_KEY` | Public anon key dari Supabase |

Jika backend belum siap, gunakan:

```env
REACT_APP_USE_MOCK_API=true
```

Jika backend sudah siap, gunakan:

```env
REACT_APP_USE_MOCK_API=false
```

---

## Script yang Tersedia

Jalankan script dari folder `frontend`.

### Menjalankan development server

```bash
npm start
```

### Build production

```bash
npm run build
```

Hasil build akan masuk ke folder:

```text
frontend/build/
```

---

## Alur Singkat Aplikasi

1. User membuka landing page.
2. User melakukan register atau login.
3. Setelah login, user masuk ke dashboard.
4. User dapat upload CV dan mengisi Job Description.
5. Sistem melakukan proses screening kandidat.
6. Kandidat ditampilkan dalam bentuk ranking.
7. User dapat melihat detail kandidat.
8. User dapat mengakses dan mengubah data profil.

---

## Catatan Pengembangan

- Jangan upload folder `node_modules` ke GitHub.
- Jangan upload file `.env` karena berisi konfigurasi lokal/secret.
- Gunakan `.env.example` sebagai template konfigurasi.
- Pastikan backend API sudah aktif sebelum menggunakan `REACT_APP_USE_MOCK_API=false`.
- Jika hanya ingin testing tampilan frontend, aktifkan mock API dengan `REACT_APP_USE_MOCK_API=true`.
- Project ini menggunakan `react-scripts`, jadi command utama untuk menjalankan frontend adalah `npm start`.

---

## Rekomendasi `.gitignore`

Pastikan file berikut tidak ikut di-upload ke GitHub:

```gitignore
node_modules/
build/
dist/
.env
.env.local
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.DS_Store
.vscode/
.idea/
```

---

## Repository

Repository tujuan:

```text
https://github.com/Temlearnt/Capstone_Project
```
