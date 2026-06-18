# Integrasi Frontend Recruitly ke FastAPI

Frontend sekarang diarahkan ke endpoint FastAPI seperti yang muncul di Swagger:

- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`
- `POST /auth/logout`
- `POST /upload/`
- `GET /status/{screening_id}`
- `GET /screen/{screening_id}/status`
- `GET /screen/{screening_id}/result`
- `GET /history/`

## Cara menjalankan

1. Jalankan FastAPI, contoh:

   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. Pastikan FastAPI mengaktifkan CORS untuk alamat frontend, contoh:

   ```python
   from fastapi.middleware.cors import CORSMiddleware

   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:3000"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

3. Di folder `frontend`, buat file `.env`:

   ```env
   REACT_APP_API_URL=http://localhost:8000
   REACT_APP_USE_MOCK_API=false
   ```

4. Jalankan frontend:

   ```bash
   npm install
   npm start
   ```

## Catatan penting

Frontend akan otomatis logout jika FastAPI mengembalikan HTTP `401` atau `403`.
Untuk fitur “login di device lain membuat device lama logout”, backend harus menyimpan session/token aktif per user dan menolak token lama dengan `401` atau `403`.
