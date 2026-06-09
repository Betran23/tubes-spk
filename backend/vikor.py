from fastapi import HTTPException, status
from sqlalchemy.orm import Session

import crud
import models


def validation_error(message: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message": message})


def validate_v(v: float) -> float:
    if v < 0 or v > 1:
        raise validation_error("nilai v harus berada pada rentang 0 sampai 1")
    return v


def round_metric(value: float) -> float:
    return round(float(value), 6)


def load_ready_data(db: Session) -> tuple[list[models.Alternative], list[models.Criterion], dict[tuple[int, int], float]]:
    alternatives = crud.get_alternatives(db)
    criteria = crud.get_criteria(db)

    if not alternatives:
        raise validation_error("perhitungan VIKOR tidak dapat dilakukan karena alternatif masih kosong")
    if not criteria:
        raise validation_error("perhitungan VIKOR tidak dapat dilakukan karena kriteria masih kosong")

    total_weight = sum(criterion.weight for criterion in criteria)
    if abs(total_weight - 1.0) > 0.000001:
        raise validation_error(f"total bobot kriteria harus sama dengan 1.0, saat ini {total_weight}")

    scores = db.query(models.Score).all()
    score_values = {(score.alternative_id, score.criterion_id): score.value for score in scores}
    missing = [
        {"alternative_id": alternative.id, "criterion_id": criterion.id}
        for alternative in alternatives
        for criterion in criteria
        if (alternative.id, criterion.id) not in score_values
    ]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "scores belum lengkap untuk semua kombinasi alternatif dan kriteria", "missing": missing},
        )

    return alternatives, criteria, score_values


def calculate_vikor(db: Session, v: float = 0.5) -> dict:
    v = validate_v(v)
    alternatives, criteria, score_values = load_ready_data(db)

    criterion_ranges = {}
    for criterion in criteria:
        values = [score_values[(alternative.id, criterion.id)] for alternative in alternatives]
        if criterion.type == "benefit":
            best = max(values)
            worst = min(values)
        else:
            best = min(values)
            worst = max(values)
        criterion_ranges[criterion.id] = {"best": best, "worst": worst, "denominator": abs(best - worst)}

    rows = []
    for alternative in alternatives:
        normalized_scores = []
        weighted_values = []
        for criterion in criteria:
            value = score_values[(alternative.id, criterion.id)]
            ranges = criterion_ranges[criterion.id]
            denominator = ranges["denominator"]
            if denominator == 0:
                normalized = 0
            elif criterion.type == "benefit":
                normalized = (ranges["best"] - value) / denominator
            else:
                normalized = (value - ranges["best"]) / denominator
            weighted = criterion.weight * normalized
            weighted_values.append(weighted)
            normalized_scores.append(
                {
                    "criterion_id": criterion.id,
                    "criterion_code": criterion.code,
                    "raw_value": round_metric(value),
                    "normalized": round_metric(normalized),
                    "weighted": round_metric(weighted),
                }
            )
        s_value = sum(weighted_values)
        r_value = max(weighted_values) if weighted_values else 0
        rows.append(
            {
                "alternative_id": alternative.id,
                "alternative_code": alternative.code,
                "alternative_name": alternative.name,
                "scores": normalized_scores,
                "S": s_value,
                "R": r_value,
            }
        )

    s_values = [row["S"] for row in rows]
    r_values = [row["R"] for row in rows]
    s_min, s_max = min(s_values), max(s_values)
    r_min, r_max = min(r_values), max(r_values)
    s_denominator = s_max - s_min
    r_denominator = r_max - r_min

    for row in rows:
        s_component = 0 if s_denominator == 0 else (row["S"] - s_min) / s_denominator
        r_component = 0 if r_denominator == 0 else (row["R"] - r_min) / r_denominator
        row["Q"] = (v * s_component) + ((1 - v) * r_component)

    ranking = sorted(rows, key=lambda item: (-item["Q"], -item["S"], -item["R"], item["alternative_id"]))
    for index, row in enumerate(ranking, start=1):
        row["rank"] = index
        row["S"] = round_metric(row["S"])
        row["R"] = round_metric(row["R"])
        row["Q"] = round_metric(row["Q"])

    return {
        "v": v,
        "criteria": [
            {
                "id": criterion.id,
                "code": criterion.code,
                "name": criterion.name,
                "weight": round_metric(criterion.weight),
                "type": criterion.type,
                "best": round_metric(criterion_ranges[criterion.id]["best"]),
                "worst": round_metric(criterion_ranges[criterion.id]["worst"]),
            }
            for criterion in criteria
        ],
        "results": ranking,
    }


def get_ranking(db: Session, v: float = 0.5) -> dict:
    calculation = calculate_vikor(db, v)
    return {
        "v": calculation["v"],
        "ranking": [
            {
                "rank": row["rank"],
                "alternative_id": row["alternative_id"],
                "alternative_code": row["alternative_code"],
                "alternative_name": row["alternative_name"],
                "S": round_metric(row["S"]),
                "R": round_metric(row["R"]),
                "Q": round_metric(row["Q"]),
            }
            for row in calculation["results"]
        ],
    }


def get_compromise(db: Session, v: float = 0.5) -> dict:
    ranking_payload = get_ranking(db, v)
    ranking = ranking_payload["ranking"]
    best = ranking[0]
    if len(ranking) == 1:
        return {"v": ranking_payload["v"], "compromise_solutions": [best], "acceptable_advantage": True, "acceptable_stability": True}

    dq = 1 / (len(ranking) - 1)
    acceptable_advantage = (ranking[1]["Q"] - ranking[0]["Q"]) >= dq
    min_s_id = min(ranking, key=lambda row: row["S"])["alternative_id"]
    min_r_id = min(ranking, key=lambda row: row["R"])["alternative_id"]
    acceptable_stability = best["alternative_id"] in {min_s_id, min_r_id}

    if acceptable_advantage and acceptable_stability:
        solutions = [best]
    elif not acceptable_advantage:
        solutions = [row for row in ranking if row["Q"] - best["Q"] < dq]
    else:
        solutions = ranking[:2]

    return {
        "v": ranking_payload["v"],
        "compromise_solutions": solutions,
        "acceptable_advantage": acceptable_advantage,
        "acceptable_stability": acceptable_stability,
        "dq": dq,
    }
