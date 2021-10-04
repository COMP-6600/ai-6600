"""add batch table

Revision ID: f71266695671
Revises: 1241920f1f7e
Create Date: 2021-10-03 22:26:05.433466

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f71266695671'
down_revision = '1241920f1f7e'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'batch',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('batch', sa.String(32), nullable=False, unique=True),
        sa.Column('created', sa.DateTime(), nullable=False),
        sa.Column('image_original', sa.LargeBinary(), nullable=False),
        sa.Column('image_processed', sa.LargeBinary())
    )


def downgrade():
    pass
