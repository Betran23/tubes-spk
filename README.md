# SPK VIKOR App

Aplikasi ini adalah sistem pendukung keputusan menggunakan metode VIKOR.

Project terdiri dari dua bagian:

- `backend/`: API menggunakan Python, FastAPI, PostgreSQL, SQLAlchemy, dan Alembic.
- `frontend/`: Dashboard menggunakan React + Vite dengan style neo brutalism.

## Struktur Project

```text
SPK/
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   ├── vikor.py
│   ├── requirements.txt
│   ├── .env
│   ├── alembic.ini
│   ├── migrations/
│   └── routers/
├── frontend/
│   ├── package.json
│   ├── index.html
│   ├── vite.config.js
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── api.js
│       └── styles.css
└── README.md
```

## Kebutuhan Software

Pastikan sudah install:

- Python 3.10 atau lebih baru
- Node.js 18 atau lebih baru
- PostgreSQL
- npm

## Menjalankan Backend

1. Masuk ke folder backend:

```bash
cd backend
```

2. Buat virtual environment:

```bash
python -m venv venv
```

3. Aktifkan virtual environment.

Windows:

```bash
venv\Scripts\activate
```

Mac/Linux:

```bash
source venv/bin/activate
```

4. Install dependency backend:

```bash
pip install -r requirements.txt
```

5. Buat database PostgreSQL:

```sql
CREATE DATABASE vikor_db;
```

6. Edit file `backend/.env` sesuai username dan password PostgreSQL kamu:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/vikor_db
```

Contoh:

```env
DATABASE_URL=postgresql://postgres:admin123@localhost:5432/vikor_db
```

7. Jalankan migration:

```bash
python -m alembic upgrade head
```

8. Jalankan backend:

```bash
python -m uvicorn main:app --reload
```

Backend berjalan di:

```text
http://localhost:8000
```

Dokumentasi API otomatis:

```text
http://localhost:8000/docs
```

## Menjalankan Frontend

Buka terminal baru, lalu jalankan:

```bash
cd frontend
npm install
npm run dev
```

Frontend berjalan di:

```text
http://localhost:5173
```

Pastikan backend sudah berjalan di `http://localhost:8000` sebelum memakai frontend.

## Alur Menjalankan Lengkap

Terminal 1 untuk backend:

```bash
cd backend
venv\Scripts\activate
python -m uvicorn main:app --reload
```

Terminal 2 untuk frontend:

```bash
cd frontend
npm run dev
```

Lalu buka:

```text
http://localhost:5173
```

## Endpoint Backend

Alternatives:

```text
GET    /api/alternatives
GET    /api/alternatives/{id}
POST   /api/alternatives
PUT    /api/alternatives/{id}
DELETE /api/alternatives/{id}
```

Criteria:

```text
GET    /api/criteria
GET    /api/criteria/{id}
POST   /api/criteria
PUT    /api/criteria/{id}
DELETE /api/criteria/{id}
```

Scores:

```text
GET    /api/scores
POST   /api/scores
PUT    /api/scores/{id}
DELETE /api/scores/{id}
GET    /api/scores/matrix
```

Calculation:

```text
GET /api/vikor/calculate?v=0.5
GET /api/vikor/ranking?v=0.5
GET /api/vikor/compromise?v=0.5
```

## Cara Mengubah URL API Frontend

Secara default frontend mengarah ke:

```text
http://localhost:8000/api
```

Kalau backend pindah URL, buat file `frontend/.env`:

```env
VITE_API_BASE_URL=http://localhost:8000/api
```

Setelah mengubah `.env`, restart frontend:

```bash
npm run dev
```

## Cara Mengubah Tampilan UI

File utama style frontend ada di:

```text
frontend/src/styles.css
```

Bagian warna utama ada di `:root`:

```css
:root {
  --ink: #111111;
  --paper: #fff8df;
  --hot: #ff4d00;
  --acid: #d6ff00;
  --sky: #7bdcff;
  --pink: #ff77bd;
}
```

Kalau ingin mengubah warna neo brutalism, ubah nilai variable tersebut.

## Cara Mengubah Logic Frontend

File utama halaman frontend:

```text
frontend/src/App.jsx
```

File untuk request ke backend:

```text
frontend/src/api.js
```

Kalau endpoint backend berubah, biasanya cukup ubah `frontend/src/api.js`.

## Fitur Import CSV

Frontend memiliki menu `Import CSV` untuk memasukkan data dari file `.csv` tanpa menulis SQL manual.

Alurnya:

1. Buka frontend di `http://localhost:5173`.
2. Pilih tab `Import CSV`.
3. Upload file `.csv`.
4. Pilih mode import:
   - `Replace semua data lama`: hapus data lama lalu isi dari CSV.
   - `Tambah/update data`: data lama tetap ada, data dengan kode sama akan di-update.
5. Masukkan jumlah kriteria.
6. Pilih kolom untuk kode alternatif dan nama alternatif. Jika kode alternatif pada CSV tidak unik, gunakan kolom kode tambahan opsional, misalnya `NAMA + KODE`.
7. Untuk setiap kriteria, isi kode, nama, bobot, tipe `benefit/cost`, dan kolom nilai dari CSV.
8. Cek preview data.
9. Klik `Konfirmasi Import CSV`.

Validasi import:

- Total bobot kriteria harus `1.0`.
- Kode alternatif tidak boleh kosong.
- Kode alternatif hasil mapping tidak boleh duplikat. Jika satu kolom duplikat, gabungkan dengan kolom tambahan opsional.
- Setiap kolom nilai kriteria harus berupa angka.
- Setiap kriteria harus punya tepat satu kolom nilai dari CSV.

Backend endpoint untuk fitur ini:

```text
POST /api/import/csv/preview
POST /api/import/csv/commit
```

## Cara Mengubah Backend

File penting backend:

- `backend/main.py`: konfigurasi FastAPI, router, dan CORS.
- `backend/database.py`: koneksi database.
- `backend/models.py`: struktur tabel database.
- `backend/schemas.py`: validasi request dan response.
- `backend/crud.py`: logic CRUD database.
- `backend/vikor.py`: logic perhitungan VIKOR.
- `backend/routers/`: endpoint API.

## Jika Mengubah Model Database

Kalau mengubah `backend/models.py`, buat migration baru:

```bash
cd backend
python -m alembic revision --autogenerate -m "deskripsi perubahan"
python -m alembic upgrade head
```

Contoh:

```bash
python -m alembic revision --autogenerate -m "add description to criteria"
python -m alembic upgrade head
```

## Troubleshooting

### Backend error: `DATABASE_URL belum diatur di file .env`

Pastikan file `backend/.env` ada dan berisi:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/vikor_db
```

### Backend error: database tidak ditemukan

Buat database PostgreSQL dulu:

```sql
CREATE DATABASE vikor_db;
```

### Backend error: password authentication failed

Username atau password PostgreSQL di `backend/.env` salah. Sesuaikan bagian ini:

```env
postgresql://username:password@localhost:5432/vikor_db
```

### Command `uvicorn` atau `alembic` tidak dikenali

Gunakan format `python -m`:

```bash
python -m uvicorn main:app --reload
python -m alembic upgrade head
```

### Frontend tidak bisa mengambil data dari backend

Pastikan backend berjalan:

```text
http://localhost:8000/docs
```

Pastikan frontend mengarah ke URL API yang benar di `frontend/src/api.js` atau `frontend/.env`.

### Error CORS

Cek `backend/main.py`. Origin frontend harus terdaftar:

```python
allow_origins=["http://localhost:5173"]
```

### Perhitungan VIKOR gagal karena total bobot

Total bobot kriteria harus sama dengan `1.0`.

Contoh valid:

```text
0.25 + 0.25 + 0.25 + 0.25 = 1.0
```

Jika input bobot dalam persen, backend akan mengubah otomatis:

```text
25 menjadi 0.25
```

### Perhitungan VIKOR gagal karena scores belum lengkap

Setiap alternatif harus punya nilai untuk semua kriteria.

Contoh: jika ada 3 alternatif dan 4 kriteria, maka harus ada `3 x 4 = 12` data scores.

## Build Production Frontend

Untuk membuat build frontend:

```bash
cd frontend
npm run build
```

Hasil build ada di:

```text
frontend/dist/
```

## Verifikasi Cepat

Backend:

```bash
cd backend
python -m alembic heads
python -m uvicorn main:app --reload
```

Frontend:

```bash
cd frontend
npm run build
npm run dev
```
