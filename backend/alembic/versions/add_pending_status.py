"""add pending status to problemstatus enum

Revision ID: add_pending_status
Revises: 68f49b330e87
Create Date: 2026-04-17 02:50:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_pending_status'
down_revision = '68f49b330e87'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add 'pending' to problemstatus enum
    op.execute("ALTER TYPE problemstatus ADD VALUE IF NOT EXISTS 'pending'")


def downgrade() -> None:
    # Cannot remove enum values in PostgreSQL easily
    # Would require recreating the enum and updating all references
    pass
