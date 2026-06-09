from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

import crud
import schemas
from database import get_db

router = APIRouter(prefix="/alternatives", tags=["Alternatives"])


@router.get("", response_model=list[schemas.AlternativeResponse])
def list_alternatives(db: Session = Depends(get_db)):
    return crud.get_alternatives(db)


@router.get("/{alternative_id}", response_model=schemas.AlternativeResponse)
def get_alternative(alternative_id: int, db: Session = Depends(get_db)):
    alternative = crud.get_alternative(db, alternative_id)
    if not alternative:
        raise crud.not_found("Alternative")
    return alternative


@router.post("", response_model=schemas.AlternativeResponse, status_code=status.HTTP_201_CREATED)
def create_alternative(payload: schemas.AlternativeCreate, db: Session = Depends(get_db)):
    return crud.create_alternative(db, payload)


@router.put("/{alternative_id}", response_model=schemas.AlternativeResponse)
def update_alternative(alternative_id: int, payload: schemas.AlternativeUpdate, db: Session = Depends(get_db)):
    return crud.update_alternative(db, alternative_id, payload)


@router.delete("/{alternative_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_alternative(alternative_id: int, db: Session = Depends(get_db)):
    crud.delete_alternative(db, alternative_id)
    return None
