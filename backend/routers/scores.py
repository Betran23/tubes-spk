from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

import crud
import schemas
from database import get_db

router = APIRouter(prefix="/scores", tags=["Scores"])


@router.get("", response_model=list[schemas.ScoreResponse])
def list_scores(db: Session = Depends(get_db)):
    return crud.get_scores(db)


@router.get("/matrix", response_model=list[schemas.ScoreMatrixRow])
def get_score_matrix(db: Session = Depends(get_db)):
    return crud.get_score_matrix(db)


@router.post("", response_model=schemas.ScoreResponse, status_code=status.HTTP_201_CREATED)
def create_score(payload: schemas.ScoreCreate, db: Session = Depends(get_db)):
    return crud.create_score(db, payload)


@router.put("/{score_id}", response_model=schemas.ScoreResponse)
def update_score(score_id: int, payload: schemas.ScoreUpdate, db: Session = Depends(get_db)):
    return crud.update_score(db, score_id, payload)


@router.delete("/{score_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_score(score_id: int, db: Session = Depends(get_db)):
    crud.delete_score(db, score_id)
    return None
