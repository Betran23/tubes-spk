from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

import crud
import schemas
from database import get_db

router = APIRouter(prefix="/criteria", tags=["Criteria"])


@router.get("", response_model=list[schemas.CriterionResponse])
def list_criteria(db: Session = Depends(get_db)):
    return crud.get_criteria(db)


@router.get("/{criterion_id}", response_model=schemas.CriterionResponse)
def get_criterion(criterion_id: int, db: Session = Depends(get_db)):
    criterion = crud.get_criterion(db, criterion_id)
    if not criterion:
        raise crud.not_found("Criterion")
    return criterion


@router.post("", response_model=schemas.CriterionResponse, status_code=status.HTTP_201_CREATED)
def create_criterion(payload: schemas.CriterionCreate, db: Session = Depends(get_db)):
    return crud.create_criterion(db, payload)


@router.put("/{criterion_id}", response_model=schemas.CriterionResponse)
def update_criterion(criterion_id: int, payload: schemas.CriterionUpdate, db: Session = Depends(get_db)):
    return crud.update_criterion(db, criterion_id, payload)


@router.delete("/{criterion_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_criterion(criterion_id: int, db: Session = Depends(get_db)):
    crud.delete_criterion(db, criterion_id)
    return None
