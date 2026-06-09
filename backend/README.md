# Backend VIKOR

Backend ini menggunakan Python, FastAPI, Uvicorn, PostgreSQL, SQLAlchemy, Alembic, Pydantic, psycopg2-binary, dan python-dotenv.

## Cara Menjalankan

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

4. Install dependencies:

```bash
pip install -r requirements.txt
```

5. Buat database PostgreSQL:

```sql
CREATE DATABASE vikor_db;
```

6. Isi file `.env`:

```text
DATABASE_URL=postgresql://username:password@localhost:5432/vikor_db
```

7. Jalankan migration:

```bash
alembic upgrade head
```

Jika ingin membuat migration ulang dari model, gunakan:

```bash
alembic init migrations
alembic revision --autogenerate -m "create initial tables"
alembic upgrade head
```

Catatan: scaffold ini sudah menyertakan folder `migrations/` dan migration awal, jadi `alembic init migrations` tidak perlu dijalankan lagi kecuali ingin membuat ulang konfigurasi Alembic.

8. Jalankan server:

```bash
uvicorn main:app --reload
```

Backend dapat diakses di `http://localhost:8000`.

Dokumentasi API otomatis dapat diakses di `http://localhost:8000/docs`.

## Endpoint Minimal

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
