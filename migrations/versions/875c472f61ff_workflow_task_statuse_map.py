"""workflow task statuse map

Revision ID: 875c472f61ff
Revises: 573c1cd0721f
Create Date: 2021-11-23 16:35:29.172951

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '875c472f61ff'
down_revision = '573c1cd0721f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('workflow', sa.Column('_task_statuses_map', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('workflow', '_task_statuses_map')
    # ### end Alembic commands ###
