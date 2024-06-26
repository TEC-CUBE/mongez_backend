"""empty message

Revision ID: d1b737a8e7b3
Revises: 3956fb68b17a
Create Date: 2024-06-20 21:14:47.762903

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd1b737a8e7b3'
down_revision = '3956fb68b17a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('branch', schema=None) as batch_op:
        batch_op.add_column(sa.Column('status', sa.String(length=20), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('branch', schema=None) as batch_op:
        batch_op.drop_column('status')

    # ### end Alembic commands ###
