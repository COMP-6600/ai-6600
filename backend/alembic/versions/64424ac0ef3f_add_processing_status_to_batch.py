"""add processing status to batch

Revision ID: 64424ac0ef3f
Revises: f71266695671
Create Date: 2021-10-05 04:04:52.240804

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '64424ac0ef3f'
down_revision = 'f71266695671'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('batch', sa.Column('process_status', sa.String(50), nullable=False))


def downgrade():
    op.drop_column('batch', 'process_status')
