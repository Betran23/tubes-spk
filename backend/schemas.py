from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


def normalize_weight(value: float) -> float:
    if value <= 0:
        raise ValueError("weight harus lebih dari 0")
    if value > 100:
        raise ValueError("weight persen tidak boleh lebih dari 100")
    return value / 100 if value > 1 else value


class AlternativeBase(BaseModel):
    code: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)


class AlternativeCreate(AlternativeBase):
    pass


class AlternativeUpdate(BaseModel):
    code: Optional[str] = Field(default=None, min_length=1)
    name: Optional[str] = Field(default=None, min_length=1)


class AlternativeResponse(AlternativeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class CriterionBase(BaseModel):
    code: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    weight: float
    type: str

    @field_validator("weight")
    @classmethod
    def validate_weight(cls, value: float) -> float:
        return normalize_weight(value)

    @field_validator("type")
    @classmethod
    def validate_type(cls, value: str) -> str:
        normalized = value.lower()
        if normalized not in {"benefit", "cost"}:
            raise ValueError("type harus benefit atau cost")
        return normalized


class CriterionCreate(CriterionBase):
    pass


class CriterionUpdate(BaseModel):
    code: Optional[str] = Field(default=None, min_length=1)
    name: Optional[str] = Field(default=None, min_length=1)
    weight: Optional[float] = None
    type: Optional[str] = None

    @field_validator("weight")
    @classmethod
    def validate_weight(cls, value: Optional[float]) -> Optional[float]:
        if value is None:
            return value
        return normalize_weight(value)

    @field_validator("type")
    @classmethod
    def validate_type(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        normalized = value.lower()
        if normalized not in {"benefit", "cost"}:
            raise ValueError("type harus benefit atau cost")
        return normalized


class CriterionResponse(CriterionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class ScoreBase(BaseModel):
    alternative_id: int
    criterion_id: int
    value: float


class ScoreCreate(ScoreBase):
    pass


class ScoreUpdate(BaseModel):
    alternative_id: Optional[int] = None
    criterion_id: Optional[int] = None
    value: Optional[float] = None


class ScoreResponse(ScoreBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class ScoreMatrixCell(BaseModel):
    criterion_id: int
    criterion_code: str
    criterion_name: str
    value: Optional[float]


class ScoreMatrixRow(BaseModel):
    alternative_id: int
    alternative_code: str
    alternative_name: str
    scores: list[ScoreMatrixCell]
