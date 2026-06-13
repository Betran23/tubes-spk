from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

import models
from database import get_db


class DeleteDataRequest(BaseModel):
    target: Literal["all", "scores", "alternatives", "criteria"]
    confirm: str


class DeleteDataResponse(BaseModel):
    target: str
    deleted: dict[str, int]


router = APIRouter(prefix="/maintenance", tags=["Maintenance"])

TARGET_MODELS = {
    "scores": [models.Score],
    "alternatives": [models.Score, models.Alternative],
    "criteria": [models.Score, models.Criterion],
    "all": [models.Score, models.Criterion, models.Alternative],
}


@router.delete("/data", response_model=DeleteDataResponse)
def delete_data(payload: DeleteDataRequest, db: Session = Depends(get_db)):
    if payload.confirm != "HAPUS":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "ketik HAPUS untuk konfirmasi"},
        )

    deleted = {}
    for model in TARGET_MODELS[payload.target]:
        deleted[model.__tablename__] = db.query(model).delete()

    db.commit()
    return DeleteDataResponse(target=payload.target, deleted=deleted)
