"""create initial tables

Revision ID: 20260608_0001
Revises:
Create Date: 2026-06-08
"""
from alembic import op
import sqlalchemy as sa

revision = "20260608_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "alternatives",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_alternatives_code"), "alternatives", ["code"], unique=True)
    op.create_index(op.f("ix_alternatives_id"), "alternatives", ["id"], unique=False)

    op.create_table(
        "criteria",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("type IN ('benefit', 'cost')", name="ck_criteria_type"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_criteria_code"), "criteria", ["code"], unique=True)
    op.create_index(op.f("ix_criteria_id"), "criteria", ["id"], unique=False)

    op.create_table(
        "scores",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("alternative_id", sa.Integer(), nullable=False),
        sa.Column("criterion_id", sa.Integer(), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["alternative_id"], ["alternatives.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["criterion_id"], ["criteria.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("alternative_id", "criterion_id", name="uq_scores_alternative_criterion"),
    )
    op.create_index(op.f("ix_scores_alternative_id"), "scores", ["alternative_id"], unique=False)
    op.create_index(op.f("ix_scores_criterion_id"), "scores", ["criterion_id"], unique=False)
    op.create_index(op.f("ix_scores_id"), "scores", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_scores_id"), table_name="scores")
    op.drop_index(op.f("ix_scores_criterion_id"), table_name="scores")
    op.drop_index(op.f("ix_scores_alternative_id"), table_name="scores")
    op.drop_table("scores")
    op.drop_index(op.f("ix_criteria_id"), table_name="criteria")
    op.drop_index(op.f("ix_criteria_code"), table_name="criteria")
    op.drop_table("criteria")
    op.drop_index(op.f("ix_alternatives_id"), table_name="alternatives")
    op.drop_index(op.f("ix_alternatives_code"), table_name="alternatives")
    op.drop_table("alternatives")
