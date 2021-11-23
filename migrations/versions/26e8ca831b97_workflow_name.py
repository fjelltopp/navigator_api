"""workflow name

Revision ID: 26e8ca831b97
Revises: 9a0a2eabc879
Create Date: 2021-11-09 16:06:03.486300

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '26e8ca831b97'
down_revision = '9a0a2eabc879'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('workflow', sa.Column('name', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('workflow', 'name')
    # ### end Alembic commands ###
