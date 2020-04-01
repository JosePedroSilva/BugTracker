"""topic column on Ticket

Revision ID: dfa422bbaa4e
Revises: dd14d0e09f99
Create Date: 2020-04-01 10:33:37.811462

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dfa422bbaa4e'
down_revision = 'dd14d0e09f99'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tickets', sa.Column('topic', sa.String(length=64), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tickets', 'topic')
    # ### end Alembic commands ###