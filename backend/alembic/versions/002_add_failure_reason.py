"""Add failure_reason to connections

Revision ID: 002_add_failure_reason
Revises: 001_initial
Create Date: 2024-01-15 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002_add_failure_reason'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check if column exists before adding it
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    columns = [col['name'] for col in inspector.get_columns('connections')]
    
    if 'failure_reason' not in columns:
        op.add_column('connections', sa.Column('failure_reason', sa.String(), nullable=True))
        print("Added failure_reason column to connections table")


def downgrade() -> None:
    op.drop_column('connections', 'failure_reason')

