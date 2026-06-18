# Model Development Workspace

Direktori ini (`/model`) khusus digunakan untuk riset, pengembangan, kuantisasi (ONNX), dan evaluasi model-model *Machine Learning* / *Artificial Intelligence* (seperti NER, SBERT, dan Clustering) sebelum diintegrasikan ke *backend* utama aplikasi.

Semua pengujian dilakukan di lingkungan lokal menggunakan Jupyter Notebook dengan konfigurasi Python *virtual environment* (`.venv`) yang terisolasi.

---

## 🛠️ Persyaratan Sistem
- **Sistem Operasi**: Windows (Direkomendasikan)
- **Python**: Versi 3.10 atau lebih baru.
- **Terminal**: PowerShell atau Command Prompt.

---

## 🚀 Cara Setup Environment Lokal (.venv)

Agar model berjalan mulus tanpa konflik dengan proyek lain, Anda wajib menggunakan lingkungan virtual (Virtual Environment). Ikuti langkah-langkah di bawah ini secara persis:

### 1. Buka Terminal di Folder Model
Pastikan terminal Anda sudah berada persis di dalam direktori `model/`:
```powershell
cd d:\Hasil_Coding\Capstone_Project\model
```

### 2. Buat Virtual Environment
Jalankan perintah berikut untuk membuat folder `.venv` baru:
```powershell
python -m venv .venv
```
*Tunggu beberapa detik hingga folder `.venv` muncul di direktori Anda.*

### 3. Aktifkan Virtual Environment
Untuk Windows (PowerShell/CMD), jalankan:
```powershell
.\.venv\Scripts\activate
```
*(Ciri-ciri berhasil: Akan muncul tulisan `(.venv)` berwarna hijau di depan kursor terminal Anda).*

---

## 📦 Instalasi Dependensi (Library)

Proyek ini sangat bergantung pada pustaka kalkulasi tensor dan NLP. Karena kita menggunakan versi GPU/CUDA untuk mempercepat kalkulasi (khususnya untuk `torch`), urutan instalasi di bawah ini sangat penting!

Pastikan `.venv` Anda dalam status **Aktif** sebelum menjalankan perintah berikut:

### Langkah 1: Instalasi PyTorch (Versi CUDA 12.1)
Kita menggunakan versi PyTorch `2.5.1+cu121` untuk akselerasi perangkat keras. Jalankan:
```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### Langkah 2: Instalasi Pustaka Utama AI & Machine Learning
Instal seluruh *engine* pendukung (seperti ONNX, Transformers, Scikit-learn, dll):
```powershell
pip install onnxruntime==1.23.2 transformers==4.57.6 sentence-transformers==3.4.1 spacy==3.8.14
pip install scikit-learn==1.7.2 pandas==2.3.3 hdbscan==0.8.44
```

### Langkah 3: Instalasi Alat Evaluasi & Jupyter Notebook
Untuk menjalankan dan melihat simulasi evaluasi (seperti `evaluate_models.ipynb`):
```powershell
pip install seqeval==1.2.2 jupyter==1.1.1 notebook==7.5.7 ipykernel==7.2.0
```

### Langkah 4: Daftarkan Kernel ke Jupyter (Opsional tapi Penting)
Agar Jupyter Notebook mendeteksi pustaka yang baru saja kita instal di dalam `.venv`, jalankan:
```powershell
python -m ipykernel install --user --name=capstone-model-env --display-name "Python (.venv Model)"
```
*(Saat Anda membuka `.ipynb` di VSCode, pastikan Anda memilih kernel **"Python (.venv Model)"** di pojok kanan atas).*

---

## 📁 Struktur Direktori Penting

- **`onnx_NER/`** & **`onnx_SBERT/`**: Berisi file model yang telah dikompres (kuantisasi) agar ukurannya jauh lebih ringan untuk dipakai di *backend* nanti.
- **`clustering_models/`**: Folder hasil *export* model K-Means/HDBSCAN (di-*ignore* oleh Git karena ukuran/relevansi *blob*).
- **`evaluate_models.ipynb`**: Notebook simulasi utama untuk mengecek "Kepintaran" model HRD kita menggunakan sampel pelamar *dummy*.
- **`generate_evaluation_notebook.py`**: Skrip khusus untuk merancang dan merombak otomatis isi notebook evaluasi (Jangan edit manual `evaluate_models.ipynb`, editlah skrip ini!).
