"""account hierarchy

Revision ID: 4f52489e3f13
Revises: 2d5cd453cbc3
Create Date: 2019-11-09 18:50:27.513675

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4f52489e3f13'
down_revision = '2d5cd453cbc3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('account', sa.Column('parent_id', sa.Integer(), nullable=True))
    op.create_foreign_key(op.f('fk_account_parent_id_account'), 'account', 'account', ['parent_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f('fk_account_parent_id_account'), 'account', type_='foreignkey')
    op.drop_column('account', 'parent_id')
    # ### end Alembic commands ###
