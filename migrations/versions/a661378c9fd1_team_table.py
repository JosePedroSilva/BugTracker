"""team table

Revision ID: a661378c9fd1
Revises: e4cb8882c7bd
Create Date: 2020-02-15 09:24:47.316198

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a661378c9fd1'
down_revision = 'e4cb8882c7bd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('teams',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.add_column('tickets', sa.Column('team_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'tickets', 'teams', ['team_id'], ['id'])
    op.add_column('users', sa.Column('team_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'users', 'teams', ['team_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users', type_='foreignkey')
    op.drop_column('users', 'team_id')
    op.drop_constraint(None, 'tickets', type_='foreignkey')
    op.drop_column('tickets', 'team_id')
    op.drop_table('teams')
    # ### end Alembic commands ###
