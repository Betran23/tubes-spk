from typing import TypeVar

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

import models
import schemas

ModelType = TypeVar("ModelType")


def not_found(resource: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"message": f"{resource} tidak ditemukan"})


def conflict(message: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail={"message": message})


def get_alternatives(db: Session) -> list[models.Alternative]:
    return db.query(models.Alternative).order_by(models.Alternative.id).all()


def get_alternative(db: Session, alternative_id: int) -> models.Alternative | None:
    return db.query(models.Alternative).filter(models.Alternative.id == alternative_id).first()


def create_alternative(db: Session, payload: schemas.AlternativeCreate) -> models.Alternative:
    if db.query(models.Alternative).filter(models.Alternative.code == payload.code).first():
        raise conflict("code alternative sudah digunakan")
    alternative = models.Alternative(**payload.model_dump())
    db.add(alternative)
    db.commit()
    db.refresh(alternative)
    return alternative


def update_alternative(db: Session, alternative_id: int, payload: schemas.AlternativeUpdate) -> models.Alternative:
    alternative = get_alternative(db, alternative_id)
    if not alternative:
        raise not_found("Alternative")
    data = payload.model_dump(exclude_unset=True)
    if "code" in data:
        duplicate = db.query(models.Alternative).filter(models.Alternative.code == data["code"], models.Alternative.id != alternative_id).first()
        if duplicate:
            raise conflict("code alternative sudah digunakan")
    for key, value in data.items():
        setattr(alternative, key, value)
    db.commit()
    db.refresh(alternative)
    return alternative


def delete_alternative(db: Session, alternative_id: int) -> None:
    alternative = get_alternative(db, alternative_id)
    if not alternative:
        raise not_found("Alternative")
    db.delete(alternative)
    db.commit()


def get_criteria(db: Session) -> list[models.Criterion]:
    return db.query(models.Criterion).order_by(models.Criterion.id).all()


def get_criterion(db: Session, criterion_id: int) -> models.Criterion | None:
    return db.query(models.Criterion).filter(models.Criterion.id == criterion_id).first()


def create_criterion(db: Session, payload: schemas.CriterionCreate) -> models.Criterion:
    if db.query(models.Criterion).filter(models.Criterion.code == payload.code).first():
        raise conflict("code criterion sudah digunakan")
    criterion = models.Criterion(**payload.model_dump())
    db.add(criterion)
    db.commit()
    db.refresh(criterion)
    return criterion


def update_criterion(db: Session, criterion_id: int, payload: schemas.CriterionUpdate) -> models.Criterion:
    criterion = get_criterion(db, criterion_id)
    if not criterion:
        raise not_found("Criterion")
    data = payload.model_dump(exclude_unset=True)
    if "code" in data:
        duplicate = db.query(models.Criterion).filter(models.Criterion.code == data["code"], models.Criterion.id != criterion_id).first()
        if duplicate:
            raise conflict("code criterion sudah digunakan")
    for key, value in data.items():
        setattr(criterion, key, value)
    db.commit()
    db.refresh(criterion)
    return criterion


def delete_criterion(db: Session, criterion_id: int) -> None:
    criterion = get_criterion(db, criterion_id)
    if not criterion:
        raise not_found("Criterion")
    db.delete(criterion)
    db.commit()


def get_scores(db: Session) -> list[models.Score]:
    return db.query(models.Score).order_by(models.Score.id).all()


def get_score(db: Session, score_id: int) -> models.Score | None:
    return db.query(models.Score).filter(models.Score.id == score_id).first()


def validate_score_refs(db: Session, alternative_id: int, criterion_id: int) -> None:
    if not get_alternative(db, alternative_id):
        raise not_found("Alternative")
    if not get_criterion(db, criterion_id):
        raise not_found("Criterion")


def ensure_score_unique(db: Session, alternative_id: int, criterion_id: int, score_id: int | None = None) -> None:
    query = db.query(models.Score).filter(models.Score.alternative_id == alternative_id, models.Score.criterion_id == criterion_id)
    if score_id is not None:
        query = query.filter(models.Score.id != score_id)
    if query.first():
        raise conflict("kombinasi alternative_id dan criterion_id sudah ada")


def create_score(db: Session, payload: schemas.ScoreCreate) -> models.Score:
    validate_score_refs(db, payload.alternative_id, payload.criterion_id)
    ensure_score_unique(db, payload.alternative_id, payload.criterion_id)
    score = models.Score(**payload.model_dump())
    db.add(score)
    db.commit()
    db.refresh(score)
    return score


def update_score(db: Session, score_id: int, payload: schemas.ScoreUpdate) -> models.Score:
    score = get_score(db, score_id)
    if not score:
        raise not_found("Score")
    data = payload.model_dump(exclude_unset=True)
    alternative_id = data.get("alternative_id", score.alternative_id)
    criterion_id = data.get("criterion_id", score.criterion_id)
    validate_score_refs(db, alternative_id, criterion_id)
    ensure_score_unique(db, alternative_id, criterion_id, score_id=score_id)
    for key, value in data.items():
        setattr(score, key, value)
    db.commit()
    db.refresh(score)
    return score


def delete_score(db: Session, score_id: int) -> None:
    score = get_score(db, score_id)
    if not score:
        raise not_found("Score")
    db.delete(score)
    db.commit()


def get_score_matrix(db: Session) -> list[schemas.ScoreMatrixRow]:
    alternatives = get_alternatives(db)
    criteria = get_criteria(db)
    scores = db.query(models.Score).all()
    values = {(score.alternative_id, score.criterion_id): score.value for score in scores}
    return [
        schemas.ScoreMatrixRow(
            alternative_id=alternative.id,
            alternative_code=alternative.code,
            alternative_name=alternative.name,
            scores=[
                schemas.ScoreMatrixCell(
                    criterion_id=criterion.id,
                    criterion_code=criterion.code,
                    criterion_name=criterion.name,
                    value=values.get((alternative.id, criterion.id)),
                )
                for criterion in criteria
            ],
        )
        for alternative in alternatives
    ]
