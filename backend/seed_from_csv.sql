-- Seed data dari CSV:
-- C:\Users\ASUS\Documents\Exel\Untitled spreadsheet - Sheet1.csv
--
-- Cara pakai dari folder backend:
-- psql -U postgres -d vikor_db -f seed_from_csv.sql
--
-- Catatan:
-- 1. File ini memakai perintah psql `\copy`, jadi jalankan lewat psql, bukan lewat Alembic.
-- 2. Bobot kriteria mengikuti perhitungan manual Excel:
--    C1=0.15, C2=0.25, C3=0.30, C4=0.15, C5=0.15.
-- 3. Tipe kriteria bisa kamu ubah sesuai kebutuhan sebelum menjalankan file ini.
-- 4. Kode alternatif dibuat dari gabungan NAMA + KODE agar tetap unique.
--    Contoh: NAMA "NBA 13" dan KODE "354" menjadi "NBA_13_354".

BEGIN;

TRUNCATE TABLE scores RESTART IDENTITY CASCADE;
TRUNCATE TABLE criteria RESTART IDENTITY CASCADE;
TRUNCATE TABLE alternatives RESTART IDENTITY CASCADE;

INSERT INTO criteria (code, name, weight, type)
VALUES
  ('C1', 'BT N', 0.15, 'cost'),
  ('C2', 'Ketidakseimbangan Beban', 0.25, 'cost'),
  ('C3', 'Persentase', 0.30, 'cost'),
  ('C4', 'Tegangan Ujung', 0.15, 'benefit'),
  ('C5', 'Deviasi Tegangan Fasa Netral', 0.15, 'cost')
ON CONFLICT (code) DO UPDATE SET
  name = EXCLUDED.name,
  weight = EXCLUDED.weight,
  type = EXCLUDED.type,
  updated_at = now();

CREATE TEMP TABLE raw_vikor_import (
  kode text,
  nama text,
  bt_n double precision,
  ketidakseimbangan_beban double precision,
  persentase double precision,
  tegangan_ujung double precision,
  deviasi_tegangan_fasa_netral double precision
) ON COMMIT DROP;

\copy raw_vikor_import (kode, nama, bt_n, ketidakseimbangan_beban, persentase, tegangan_ujung, deviasi_tegangan_fasa_netral) FROM 'C:/Users/ASUS/Documents/Exel/Untitled spreadsheet - Sheet1.csv' WITH (FORMAT csv, HEADER true);

INSERT INTO alternatives (code, name)
SELECT
  regexp_replace(upper(nama), '[^A-Z0-9]+', '_', 'g') || '_' || kode AS code,
  nama || ' - ' || kode AS name
FROM raw_vikor_import
ON CONFLICT (code) DO UPDATE SET
  name = EXCLUDED.name,
  updated_at = now();

INSERT INTO scores (alternative_id, criterion_id, value)
SELECT a.id, c.id, v.value
FROM raw_vikor_import r
JOIN alternatives a ON a.code = regexp_replace(upper(r.nama), '[^A-Z0-9]+', '_', 'g') || '_' || r.kode
JOIN LATERAL (
  VALUES
    ('C1', r.bt_n),
    ('C2', r.ketidakseimbangan_beban),
    ('C3', r.persentase),
    ('C4', r.tegangan_ujung),
    ('C5', r.deviasi_tegangan_fasa_netral)
) AS v(criterion_code, value) ON true
JOIN criteria c ON c.code = v.criterion_code
ON CONFLICT (alternative_id, criterion_id) DO UPDATE SET
  value = EXCLUDED.value,
  updated_at = now();

COMMIT;

SELECT 'alternatives' AS table_name, count(*) AS total FROM alternatives
UNION ALL
SELECT 'criteria' AS table_name, count(*) AS total FROM criteria
UNION ALL
SELECT 'scores' AS table_name, count(*) AS total FROM scores;
