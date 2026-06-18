# Kontrak API Frontend Recruitly

Frontend ini sudah disiapkan untuk backend Python/FastAPI. Base URL dibaca dari:

```env
REACT_APP_API_URL=http://localhost:5000
```

Kalau backend belum siap, pakai:

```env
REACT_APP_USE_MOCK_API=true
```

## Auth

### POST `/api/auth/register`
Request:
```json
{ "name": "Nama User", "email": "user@email.com", "password": "password123" }
```
Response yang diterima frontend:
```json
{ "access_token": "jwt", "user": { "id": "1", "name": "Nama User", "email": "user@email.com" } }
```

### POST `/api/auth/login`
Request:
```json
{ "email": "user@email.com", "password": "password123" }
```
Response sama seperti register.

### GET `/api/auth/me`
Header:
```txt
Authorization: Bearer <token>
```
Response:
```json
{ "user": { "id": "1", "name": "Nama User", "email": "user@email.com" } }
```

### POST `/api/auth/logout`
Boleh kosong. Frontend tetap menghapus sesi lokal.

## Kandidat

### GET `/api/candidates`
Response boleh salah satu:
```json
{ "candidates": [] }
```
atau langsung array:
```json
[]
```

Minimal field kandidat:
```json
{
  "id": 1,
  "name": "Budi",
  "email": "budi@email.com",
  "phone": "-",
  "location": "Jakarta",
  "position": "Frontend Developer",
  "score": 88,
  "status": "Sangat Cocok",
  "skills": ["React", "TypeScript"],
  "education": { "level": "S1", "major": "TI", "university": "UI", "gpa": "3.7", "year": "2020" },
  "experience": { "years": 3, "label": "3 tahun" },
  "scoreBreakdown": { "skill": 90, "experience": 85, "education": 80, "relevance": 88 },
  "workHistory": [],
  "cvText": "Ringkasan CV..."
}
```

Frontend juga menerima versi snake_case seperti `score_breakdown`, `work_history`, dan `cv_text`.

## Job Description

### GET `/api/job-descriptions`
Response:
```json
{
  "Frontend Developer": "Isi JD...",
  "Backend Developer": "Isi JD..."
}
```

## Upload CV dan Screening

### POST `/api/cv/upload`
Content-Type: `multipart/form-data`

Field:
- `files`: satu atau banyak file PDF
- `role`: role yang dipilih
- `job_description`: isi job description aktif

Response bebas, contoh:
```json
{ "uploaded": 3, "message": "CV uploaded" }
```

### POST `/api/screening/run`
Request:
```json
{ "role": "Frontend Developer", "job_description": "Isi JD..." }
```
Response:
```json
{ "candidates": [] }
```

Setelah endpoint ini mengembalikan kandidat, frontend otomatis update ranking/dashboard.
