"""empty message

Revision ID: 748d880b4788
Revises: d1b737a8e7b3
Create Date: 2024-06-21 14:49:28.031318

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '748d880b4788'
down_revision = 'd1b737a8e7b3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('product_category_association',
    sa.Column('product_uuid', sa.String(length=50), nullable=False),
    sa.Column('category_uuid', sa.String(length=50), nullable=False),
    sa.ForeignKeyConstraint(['category_uuid'], ['category.uuid'], ),
    sa.ForeignKeyConstraint(['product_uuid'], ['product.uuid'], ),
    sa.PrimaryKeyConstraint('product_uuid', 'category_uuid')
    )
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.drop_constraint('product_ibfk_1', type_='foreignkey')
        batch_op.drop_column('category_uuid')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.add_column(sa.Column('category_uuid', mysql.VARCHAR(collation='utf8mb3_bin', length=50), nullable=True))
        batch_op.create_foreign_key('product_ibfk_1', 'category', ['category_uuid'], ['uuid'])

    op.drop_table('product_category_association')
    # ### end Alembic commands ###
