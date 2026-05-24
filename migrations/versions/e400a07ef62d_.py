"""empty message

Revision ID: e400a07ef62d
Revises: f9657cea75fa
Create Date: 2026-05-22 15:59:08.560531

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e400a07ef62d'
down_revision: Union[str, Sequence[str], None] = 'f9657cea75fa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # =========================
    # ADD COLUMN
    # =========================
    op.add_column(
        'events',
        sa.Column('test_drive_id', sa.String(), nullable=True)
    )

    # =========================
    # MAKE APPLICATION OPTIONAL
    # =========================
    op.alter_column(
        'events',
        'application_id',
        existing_type=sa.VARCHAR(),
        nullable=True
    )

    # =========================
    # FIX ENUM (IMPORTANT)
    # =========================
    op.alter_column(
        'events',
        'type',
        existing_type=sa.Enum(
            'APPLICATION_CREATED',
            'APPLICATION_SUBMITTED',
            'APPLICATION_APPROVED',
            'APPLICATION_REJECTED',
            'APPLICATION_ARCHIVED',
            'APPLICATION_RESTORED',
            'DOCUMENT_VALIDATED',
            'DOCUMENT_REJECTED',
            name='eventtype'
        ),
        type_=sa.Enum(
            'APPLICATION_CREATED',
            'APPLICATION_SUBMITTED',
            'APPLICATION_APPROVED',
            'APPLICATION_REJECTED',
            'APPLICATION_ARCHIVED',
            'APPLICATION_RESTORED',
            'DOCUMENT_VALIDATED',
            'DOCUMENT_REJECTED',
            'TEST_DRIVE_CREATED',
            'TEST_DRIVE_CONFIRMED',
            'TEST_DRIVE_REJECTED',
            'TEST_DRIVE_CANCELLED',
            'TEST_DRIVE_COMPLETED',
            'NOTIFICATION_SENT',
            name='eventtype'
        ),
        existing_nullable=False
    )

    # =========================
    # TIMEZONE FIX
    # =========================
    op.alter_column(
        'events',
        'created_at',
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=False
    )

    # =========================
    # INDEX
    # =========================
    op.create_index(
        'ix_events_test_drive_id',
        'events',
        ['test_drive_id'],
        unique=False
    )

    # =========================
    # FOREIGN KEY (NAMED)
    # =========================
    op.create_foreign_key(
        'fk_events_test_drive_id',
        'events',
        'test_drives',
        ['test_drive_id'],
        ['id']
    )

def downgrade() -> None:
    """Downgrade schema."""

    # =========================
    # DROP FK
    # =========================
    op.drop_constraint(
        'fk_events_test_drive_id',
        'events',
        type_='foreignkey'
    )

    # =========================
    # DROP INDEX
    # =========================
    op.drop_index(
        'ix_events_test_drive_id',
        table_name='events'
    )

    # =========================
    # REVERT COLUMN TYPE
    # =========================
    op.alter_column(
        'events',
        'type',
        existing_type=sa.Enum(
            'APPLICATION_CREATED',
            'APPLICATION_SUBMITTED',
            'APPLICATION_APPROVED',
            'APPLICATION_REJECTED',
            'APPLICATION_ARCHIVED',
            'APPLICATION_RESTORED',
            'DOCUMENT_VALIDATED',
            'DOCUMENT_REJECTED',
            'TEST_DRIVE_CREATED',
            'TEST_DRIVE_CONFIRMED',
            'TEST_DRIVE_REJECTED',
            'TEST_DRIVE_CANCELLED',
            'TEST_DRIVE_COMPLETED',
            'NOTIFICATION_SENT',
            name='eventtype'
        ),
        type_=sa.Enum(
            'APPLICATION_CREATED',
            'APPLICATION_SUBMITTED',
            'APPLICATION_APPROVED',
            'APPLICATION_REJECTED',
            'APPLICATION_ARCHIVED',
            'APPLICATION_RESTORED',
            'DOCUMENT_VALIDATED',
            'DOCUMENT_REJECTED',
            name='eventtype'
        ),
        existing_nullable=False
    )

    # =========================
    # REVERT APPLICATION_ID
    # =========================
    op.alter_column(
        'events',
        'application_id',
        existing_type=sa.VARCHAR(),
        nullable=False
    )

    # =========================
    # DROP COLUMN
    # =========================
    op.drop_column('events', 'test_drive_id')
