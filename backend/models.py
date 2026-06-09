from sqlalchemy import CheckConstraint, Column, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import relationship

from database import Base


class Alternative(Base):
    __tablename__ = "alternatives"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    scores = relationship("Score", back_populates="alternative", cascade="all, delete-orphan", passive_deletes=True)


class Criterion(Base):
    __tablename__ = "criteria"
    __table_args__ = (CheckConstraint("type IN ('benefit', 'cost')", name="ck_criteria_type"),)

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    weight = Column(Float, nullable=False)
    type = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    scores = relationship("Score", back_populates="criterion", cascade="all, delete-orphan", passive_deletes=True)


class Score(Base):
    __tablename__ = "scores"
    __table_args__ = (UniqueConstraint("alternative_id", "criterion_id", name="uq_scores_alternative_criterion"),)

    id = Column(Integer, primary_key=True, index=True)
    alternative_id = Column(Integer, ForeignKey("alternatives.id", ondelete="CASCADE"), nullable=False, index=True)
    criterion_id = Column(Integer, ForeignKey("criteria.id", ondelete="CASCADE"), nullable=False, index=True)
    value = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    alternative = relationship("Alternative", back_populates="scores")
    criterion = relationship("Criterion", back_populates="scores")
