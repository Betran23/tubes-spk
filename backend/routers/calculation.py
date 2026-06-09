from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

import vikor
from database import get_db

router = APIRouter(prefix="/vikor", tags=["VIKOR"])


@router.get("/calculate")
def calculate(v: float = Query(default=0.5), db: Session = Depends(get_db)):
    return vikor.calculate_vikor(db, v)


@router.get("/ranking")
def ranking(v: float = Query(default=0.5), db: Session = Depends(get_db)):
    return vikor.get_ranking(db, v)


@router.get("/compromise")
def compromise(v: float = Query(default=0.5), db: Session = Depends(get_db)):
    return vikor.get_compromise(db, v)
