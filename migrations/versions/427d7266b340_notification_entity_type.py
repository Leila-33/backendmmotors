"""notification_entity_type

Revision ID: 427d7266b340
Revises: f56c226a9918
Create Date: 2026-07-17 14:17:08.121680

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '427d7266b340'
down_revision: Union[str, Sequence[str], None] = 'f56c226a9918'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


notification_entity_type = postgresql.ENUM(
    "QUOTE",
    "APPLICATION",
    "DOCUMENT",
    "TEST_DRIVE",
    name="notificationentitytype",
)


def upgrade() -> None:

    bind = op.get_bind()


    # =========================
    # CREATE ENUM
    # =========================

    notification_entity_type.create(
        bind,
        checkfirst=True
    )


    # =========================
    # NORMALIZE OLD VALUES
    # =========================

    op.execute("""
        UPDATE notifications
        SET entity_type = UPPER(entity_type)
        WHERE entity_type IS NOT NULL
    """)


    # =========================
    # ALTER COLUMN
    # =========================

    op.alter_column(
        "notifications",
        "entity_type",
        existing_type=sa.VARCHAR(),
        type_=notification_entity_type,
        existing_nullable=True,
        postgresql_using=(
            "entity_type::notificationentitytype"
        ),
    )



def downgrade() -> None:

    bind = op.get_bind()


    op.alter_column(
        "notifications",
        "entity_type",
        existing_type=notification_entity_type,
        type_=sa.VARCHAR(),
        existing_nullable=True,
    )


    notification_entity_type.drop(
        bind,
        checkfirst=True
    )