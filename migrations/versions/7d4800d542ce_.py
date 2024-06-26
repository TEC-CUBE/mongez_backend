"""empty message

Revision ID: 7d4800d542ce
Revises: 888483e33bcc
Create Date: 2024-06-21 17:21:49.344762

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '7d4800d542ce'
down_revision = '888483e33bcc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.drop_column('image')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.add_column(sa.Column('image', mysql.VARCHAR(collation='utf8mb3_bin', length=250), nullable=True))

    # ### end Alembic commands ###
