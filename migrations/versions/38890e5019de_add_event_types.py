"""add_event_types

Revision ID: 38890e5019de
Revises: 86489f45915a
Create Date: 2026-05-22 17:13:55.354820

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '38890e5019de'
down_revision: Union[str, Sequence[str], None] = '86489f45915a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

from sqlalchemy.dialects import postgresql
import sqlalchemy as sa


def upgrade() -> None:
    """Upgrade schema."""

    # =========================
    # CREATE ENUM TYPE FIRST
    # =========================
    event_type_enum = postgresql.ENUM(
        'APPLICATION_CREATED',
        'APPLICATION_SUBMITTED',
        'APPLICATION_APPROVED',
        'APPLICATION_REJECTED',
        'APPLICATION_ARCHIVED',
        'APPLICATION_RESTORED',
        'DOCUMENT_UPLOADED',
        'DOCUMENT_VALIDATED',
        'DOCUMENT_REJECTED',
        'TEST_DRIVE_CREATED',
        'TEST_DRIVE_CONFIRMED',
        'TEST_DRIVE_REJECTED',
        'TEST_DRIVE_CANCELLED',
        'TEST_DRIVE_COMPLETED',
        'NOTIFICATION_SENT',
        'ADMIN_ACTION',
        name='event_type'
    )

    event_type_enum.create(op.get_bind(), checkfirst=True)

    # =========================
    # ADD COLUMN USING ENUM
    # =========================
    op.add_column(
        'events',
        sa.Column(
            'type',
            event_type_enum,
            nullable=False
        )
    )


def downgrade() -> None:
    """Downgrade schema."""

    # =========================
    # DROP COLUMN
    # =========================
    op.drop_column('events', 'type')

    # =========================
    # DROP ENUM TYPE
    # =========================
    op.execute("DROP TYPE IF EXISTS event_type")