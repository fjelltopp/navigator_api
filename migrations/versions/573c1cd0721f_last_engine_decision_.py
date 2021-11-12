"""empty message

Revision ID: 573c1cd0721f
Revises: 26e8ca831b97
Create Date: 2021-11-11 14:34:57.265870

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '573c1cd0721f'
down_revision = '26e8ca831b97'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('workflow', sa.Column('last_engine_decision_id', sa.String(), nullable=True))


def downgrade():
    op.drop_column('workflow', 'last_engine_decision_id')
