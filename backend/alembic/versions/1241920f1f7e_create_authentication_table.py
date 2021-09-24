"""create authentication table

Revision ID: 1241920f1f7e
Revises: 
Create Date: 2021-09-23 11:52:42.736376

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1241920f1f7e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'authentication',
        sa.Column('instance', sa.String(32), primary_key=True),
        sa.Column('nonce', sa.String(32), nullable=False, unique=True),
        sa.Column('created', sa.DateTime(), nullable=False),
        sa.Column('expires', sa.DateTime(), nullable=False),
    )


def downgrade():
    op.drop_table('authentication')
