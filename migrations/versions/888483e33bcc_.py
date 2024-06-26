"""empty message

Revision ID: 888483e33bcc
Revises: c5e5d8d17f4a
Create Date: 2024-06-21 17:04:10.249462

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '888483e33bcc'
down_revision = 'c5e5d8d17f4a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('image', schema=None) as batch_op:
        batch_op.drop_column('description')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('image', schema=None) as batch_op:
        batch_op.add_column(sa.Column('description', mysql.VARCHAR(collation='utf8mb3_bin', length=500), nullable=True))

    # ### end Alembic commands ###
