"""empty message

Revision ID: 371866df718c
Revises: 4784d119c815
Create Date: 2013-10-24 01:42:46.212000

"""

# revision identifiers, used by Alembic.
revision = '371866df718c'
down_revision = '4784d119c815'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column('post', 'message', type_=sa.String(length=5000))


def downgrade():
    op.alter_column('post', 'message', type_=sa.String(length=1000))
