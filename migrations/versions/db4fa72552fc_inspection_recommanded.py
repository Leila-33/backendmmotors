"""inspection_recommanded

Revision ID: db4fa72552fc
Revises: 427d7266b340
Create Date: 2026-07-18 08:46:14.392008

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'db4fa72552fc'
down_revision: Union[str, Sequence[str], None] = '427d7266b340'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.alter_column(
        "inspections",
        "failures",
        existing_type=sa.Text(),
        type_=postgresql.JSONB(),
        postgresql_using="failures::jsonb",
        existing_nullable=True,
    )


    op.alter_column(
        "inspections",
        "recommended_repairs",
        existing_type=sa.Text(),
        type_=postgresql.JSONB(),
        postgresql_using="recommended_repairs::jsonb",
        existing_nullable=True,
    )


def downgrade() -> None:

    op.alter_column(
        "inspections",
        "failures",
        existing_type=postgresql.JSONB(),
        type_=sa.Text(),
        postgresql_using="failures::text",
        existing_nullable=True,
    )


    op.alter_column(
        "inspections",
        "recommended_repairs",
        existing_type=postgresql.JSONB(),
        type_=sa.Text(),
        postgresql_using="recommended_repairs::text",
        existing_nullable=True,
    )
