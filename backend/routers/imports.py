import csv
import io
import json

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

import models
from database import get_db
from schemas import normalize_weight

router = APIRouter(prefix="/import", tags=["Import CSV"])


def bad_request(message: str, extra: dict | None = None) -> HTTPException:
    detail = {"message": message}
    if extra:
        detail.update(extra)
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


async def read_csv(file: UploadFile) -> tuple[list[str], list[dict[str, str]]]:
    if not file.filename.lower().endswith(".csv"):
        raise bad_request("file harus berformat .csv")
    content = await file.read()
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise bad_request("file CSV harus memakai encoding UTF-8") from exc

    reader = csv.DictReader(io.StringIO(text))
    headers = reader.fieldnames or []
    if not headers:
        raise bad_request("CSV tidak memiliki header kolom")
    rows = [{key: (value or "").strip() for key, value in row.items()} for row in reader]
    if not rows:
        raise bad_request("CSV tidak memiliki data baris")
    return headers, rows


def require_column(headers: list[str], column: str, label: str) -> None:
    if not column or column not in headers:
        raise bad_request(f"kolom {label} tidak valid", {"column": column})


def normalize_code_part(value: str) -> str:
    return "_".join(value.strip().upper().split())


def build_alternative_code(row: dict[str, str], code_columns: list[str], row_index: int) -> str:
    parts = []
    for column in code_columns:
        value = row.get(column, "").strip()
        if not value:
            raise bad_request("kolom pembentuk kode alternatif tidak boleh kosong", {"row": row_index, "column": column})
        parts.append(normalize_code_part(value))
    return "_".join(parts)


def parse_float(value: str, row_number: int, column: str) -> float:
    try:
        return float(value)
    except ValueError as exc:
        raise bad_request("nilai kriteria harus berupa angka", {"row": row_number, "column": column, "value": value}) from exc


def validate_mapping(headers: list[str], rows: list[dict[str, str]], mapping: dict) -> dict:
    mode = mapping.get("mode")
    if mode not in {"replace", "upsert"}:
        raise bad_request("mode import harus replace atau upsert")

    alternative_code_columns = [column for column in (mapping.get("alternativeCodeColumns") or []) if column]
    if not alternative_code_columns and mapping.get("alternativeCodeColumn"):
        alternative_code_columns = [mapping.get("alternativeCodeColumn")]
    alternative_name_column = mapping.get("alternativeNameColumn")
    if not alternative_code_columns:
        raise bad_request("minimal pilih satu kolom pembentuk kode alternatif")
    for column in alternative_code_columns:
        require_column(headers, column, "kode alternatif")
    require_column(headers, alternative_name_column, "nama alternatif")

    criteria = mapping.get("criteria") or []
    if not criteria:
        raise bad_request("minimal harus ada satu kriteria")

    seen_codes = set()
    normalized_criteria = []
    for index, criterion in enumerate(criteria, start=1):
        code = (criterion.get("code") or f"C{index}").strip()
        name = (criterion.get("name") or code).strip()
        value_column = criterion.get("valueColumn")
        criterion_type = (criterion.get("type") or "").lower()
        try:
            weight = normalize_weight(float(criterion.get("weight", 0)))
        except (TypeError, ValueError) as exc:
            raise bad_request("bobot kriteria harus berupa angka lebih dari 0", {"code": code}) from exc

        if code in seen_codes:
            raise bad_request("kode kriteria tidak boleh duplikat", {"code": code})
        if criterion_type not in {"benefit", "cost"}:
            raise bad_request("tipe kriteria harus benefit atau cost", {"code": code})
        require_column(headers, value_column, f"nilai {code}")

        seen_codes.add(code)
        normalized_criteria.append({"code": code, "name": name, "weight": weight, "type": criterion_type, "valueColumn": value_column})

    total_weight = sum(criterion["weight"] for criterion in normalized_criteria)
    if abs(total_weight - 1.0) > 0.000001:
        raise bad_request("total bobot kriteria harus sama dengan 1.0", {"total_weight": total_weight})

    alternative_codes = set()
    duplicate_codes = set()
    parsed_rows = []
    for row_index, row in enumerate(rows, start=2):
        alternative_code = build_alternative_code(row, alternative_code_columns, row_index)
        alternative_name = row.get(alternative_name_column, "").strip()
        if not alternative_code:
            raise bad_request("kode alternatif tidak boleh kosong", {"row": row_index})
        if not alternative_name:
            raise bad_request("nama alternatif tidak boleh kosong", {"row": row_index})
        if alternative_code in alternative_codes:
            duplicate_codes.add(alternative_code)
        alternative_codes.add(alternative_code)

        values = {criterion["code"]: parse_float(row.get(criterion["valueColumn"], ""), row_index, criterion["valueColumn"]) for criterion in normalized_criteria}
        parsed_rows.append({"code": alternative_code, "name": alternative_name, "values": values})

    if duplicate_codes:
        raise bad_request("kode alternatif di CSV tidak boleh duplikat", {"duplicates": sorted(duplicate_codes)[:20]})

    return {"mode": mode, "criteria": normalized_criteria, "rows": parsed_rows}


@router.post("/csv/preview")
async def preview_csv(file: UploadFile = File(...)):
    headers, rows = await read_csv(file)
    return {"headers": headers, "totalRows": len(rows), "sampleRows": rows[:5]}


@router.post("/csv/commit")
async def commit_csv(payload: str = Form(...), file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        mapping = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise bad_request("payload mapping bukan JSON valid") from exc

    headers, rows = await read_csv(file)
    parsed = validate_mapping(headers, rows, mapping)

    if parsed["mode"] == "replace":
        db.query(models.Score).delete()
        db.query(models.Criterion).delete()
        db.query(models.Alternative).delete()
        db.flush()

    criteria_by_code = {criterion.code: criterion for criterion in db.query(models.Criterion).all()}
    for item in parsed["criteria"]:
        criterion = criteria_by_code.get(item["code"])
        if criterion:
            criterion.name = item["name"]
            criterion.weight = item["weight"]
            criterion.type = item["type"]
        else:
            criterion = models.Criterion(code=item["code"], name=item["name"], weight=item["weight"], type=item["type"])
            db.add(criterion)
            criteria_by_code[item["code"]] = criterion
    db.flush()

    alternatives_by_code = {alternative.code: alternative for alternative in db.query(models.Alternative).all()}
    created_scores = 0
    updated_scores = 0
    for item in parsed["rows"]:
        alternative = alternatives_by_code.get(item["code"])
        if alternative:
            alternative.name = item["name"]
        else:
            alternative = models.Alternative(code=item["code"], name=item["name"])
            db.add(alternative)
            alternatives_by_code[item["code"]] = alternative
        db.flush()

        for criterion in parsed["criteria"]:
            criterion_model = criteria_by_code[criterion["code"]]
            score = db.query(models.Score).filter(models.Score.alternative_id == alternative.id, models.Score.criterion_id == criterion_model.id).first()
            if score:
                score.value = item["values"][criterion["code"]]
                updated_scores += 1
            else:
                db.add(models.Score(alternative_id=alternative.id, criterion_id=criterion_model.id, value=item["values"][criterion["code"]]))
                created_scores += 1

    db.commit()
    return {
        "message": "import CSV berhasil",
        "mode": parsed["mode"],
        "alternatives": len(parsed["rows"]),
        "criteria": len(parsed["criteria"]),
        "scores_created": created_scores,
        "scores_updated": updated_scores,
    }
