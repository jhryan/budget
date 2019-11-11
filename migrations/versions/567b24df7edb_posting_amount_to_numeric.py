"""posting amount to numeric

Revision ID: 567b24df7edb
Revises: 4f52489e3f13
Create Date: 2019-11-10 01:40:02.383911

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '567b24df7edb'
down_revision = '4f52489e3f13'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('posting', 'amount', existing_nullable=False, existing_type=sa.Float, type_=sa.Numeric(precision=38, scale=28))


def downgrade():
    op.alter_column('posting', 'amount', existing_nullable=False, existing_type=sa.Numeric(precision=38, scale=28), type_=sa.Float)
